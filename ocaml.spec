%define build_ocamlopt	1
%ifarch ppc64
%define build_ocamlopt	0
%endif
%define build_labltk	1
%define name	ocaml
%define major	3.10
%define minor	0
%define version	%{major}.%{minor}
%define release	%mkrel 3

# we don't want the auto require to add require on the currently installed ocaml
%define _requires_exceptions ocaml

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	The Objective Caml compiler and programming environment
URL:		http://caml.inria.fr
License:	QPL & LGPL
Group:		Development/Other
Source0:	ftp://ftp.inria.fr/INRIA/cristal/caml-light/ocaml-%{major}/%{name}-%{version}.tar.bz2
Source1:	ftp://ftp.inria.fr/INRIA/cristal/caml-light/ocaml-%{major}/%{name}-%{major}-refman.html.tar.bz2
Source4:	%{name}.menu
Source5:	findlib-meta-files.tar.bz2
Patch3:		ocaml-3.00-ocamltags--no-site-start.patch
Patch6:		ocaml-3.04-do-not-add-rpath-X11R6_lib-when-using-option-L.patch
Patch7:		ocaml-3.05-no-opt-for-debug-and-profile.patch
Patch8:		ocaml-3.04-larger-buffer-for-uncaught-exception-messages.patch
Patch9:		ocaml-3.10.0-handle-tk-8.5.patch
Patch16:	ocaml-3.09.2-lib64.patch
Patch17:	ocaml-3.09.2-db4.patch
Patch18:	ocaml-3.09.3-compile-emacs-files-in-build-dir.patch

BuildRequires:	libx11-devel
BuildRequires:	ncurses-devel
BuildRequires:	tcl
BuildRequires:	tcl-devel
BuildRequires:	tk
BuildRequires:	tk-devel
BuildRequires:	emacs-bin
BuildRequires:	db4-devel

BuildRoot:	%{_tmppath}/%{name}-%{version}
Obsoletes:	ocaml-emacs
Provides:	ocaml-emacs

%package	doc
Summary:	Documentation for OCaml
Group:		Books/Computer books
Requires:	%{name} = %{version}

%package -n	camlp4
Summary:	Preprocessor for OCaml
Group:		Development/Other
Requires:	%{name} = %{version}

%package labltk
Summary:	Tk toolkit binding for OCaml
Group:		Development/Other
Requires:	%{name} = %{version}
Requires:	tk-devel
Obsoletes:  ocamltk

%package sources
Summary:	OCaml sources
Group:		Development/Other
# don't add crazy deps
AutoReqProv: No

%description
Objective Caml is a high-level, strongly-typed, functional and object-oriented
programming language from the ML family of languages.

This package comprises two batch compilers (a fast bytecode compiler and an
optimizing native-code compiler), an interactive toplevel system, Lex&Yacc
tools, a replay debugger, and a comprehensive library.

%description	doc
Documentation for OCaml

%description -n	camlp4
Preprocessor for OCaml

%description labltk
Tk toolkit binding for OCaml

%description sources
OCaml sources

%prep
%setup -q -T -b 0
%setup -q -T -D -a 1
%setup -q -T -D -a 5
%patch3 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch16 -p1 -b .lib64
%patch17 -p1 -b .db4
%patch18 -p1 -b .emacs

rm -rf `find -name .cvsignore`

%build
%ifarch alpha
echo %{optflags} | grep -q mieee || { echo "on alpha you need -mieee to compile ocaml"; exit 1; }
%endif

./configure -bindir %{_bindir} -libdir %{_libdir}/ocaml -mandir %{_mandir}/man1
make world
%if %{build_ocamlopt}
make opt opt.opt
%endif

%install
rm -rf %{buildroot}
make install BINDIR=%{buildroot}%{_bindir} LIBDIR=%{buildroot}%{_libdir}/ocaml MANDIR=%{buildroot}%{_mandir}

# remove stupid camlp4o.opt which can't work
rm -f %{buildroot}%{_bindir}/camlp4*.opt
rm -f %{buildroot}%{_mandir}/man1/camlp4*.opt.*

cd emacs; make install install-ocamltags BINDIR=%{buildroot}%{_bindir} EMACSDIR=%{buildroot}%{_datadir}/emacs/site-lisp; cd -

# fix
perl -pi -e "s|%{buildroot}||" %{buildroot}%{_libdir}/ocaml/ld.conf

%if %{build_ocamlopt}
# only keep the binary versions (which are much faster, and have no drawbacks (?))
for i in %{buildroot}%{_bindir}/*.opt ; do
  nonopt=`echo $i | sed "s/.opt$//"`
  rm -f $nonopt
  ln -s `basename $i` $nonopt
done
%endif


install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(require 'caml-font)
(autoload 'caml-mode "caml" "Caml editing mode" t)
(add-to-list 'auto-mode-alist '("\\\\.mli?$" . caml-mode))
EOF

# don't package mano man pages since we have the html files
rm -rf %{buildroot}%{_mandir}/mano

rm -f %{name}.list
n="labltk|camlp4|ocamlbrowser|tkanim"
(cd %{buildroot} ; find usr/bin ! -type d -printf "/%%p\n" | egrep -v $n) >> %{name}.list
(cd %{buildroot} ; find usr/%{_lib}/ocaml ! -type d -printf "/%%p\n" | egrep -v $n) >> %{name}.list
(cd %{buildroot} ; find usr/%{_lib}/ocaml   -type d -printf "%%%%dir /%%p\n" | egrep -v $n) >> %{name}.list

# install findlib META files
cp -pr site-lib %{buildroot}%{_libdir}/ocaml/
# ensure dynamic libraries from site-lie availability
echo '%{_libdir}/ocaml/site-lib/stublibs' >> %{buildroot}%{_libdir}/ocaml/ld.conf

# install sources
install -d -m 755 %{buildroot}%{_prefix}/src
tar xvjf %{SOURCE0} -C %{buildroot}%{_prefix}/src
mv %{buildroot}%{_prefix}/src/%{name}-%{version} %{buildroot}%{_prefix}/src/%{name}

%clean
rm -rf %{buildroot}

%files -f %{name}.list
%defattr(-,root,root)
%doc Changes LICENSE README
%{_mandir}/man1/*
#%{_menudir}/*
%{_datadir}/emacs/site-lisp/*
%{_libdir}/ocaml/site-lib
%exclude %{_libdir}/ocaml/site-lib/labltk
%exclude %{_libdir}/ocaml/site-lib/camlp4
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*

%files doc
%defattr(-,root,root)
%doc htmlman/* 
%{_mandir}/man3/*

%if %{build_labltk}
%files labltk
%defattr(-,root,root)
%doc otherlibs/labltk/README otherlibs/labltk/example*
%{_bindir}/*labltk*
%{_bindir}/ocamlbrowser
%{_libdir}/ocaml/*labltk*
%{_libdir}/ocaml/stublibs/dlllabltk.so
%{_libdir}/ocaml/stublibs/dlltkanim.so
%{_libdir}/ocaml/site-lib/labltk
%endif

%files -n camlp4
%defattr(-,root,root)
%{_bindir}/*camlp4*
%{_libdir}/ocaml/camlp4
%{_libdir}/ocaml/site-lib/camlp4

%files sources
%defattr(-,root,root)
%{_prefix}/src/%{name}
