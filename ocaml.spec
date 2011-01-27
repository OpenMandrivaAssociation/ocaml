%define build_ocamlopt	1
%ifarch ppc64 %mips %arm
%define build_ocamlopt	0
%endif
%define build_labltk	1
%define major	3.12
%define minor	0

# we don't want the auto require to add require on the currently installed ocaml
%define _requires_exceptions ocaml

Name:		ocaml
Version:	3.12.0
Release:	%mkrel 2
Summary:	The Objective Caml compiler and programming environment
URL:		http://caml.inria.fr
License:	QPL with exceptions and LGPLv2 with exceptions
Group:		Development/Other
Source0:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{version}.tar.bz2
Source1:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{major}-refman.html.tar.gz

# IMPORTANT:
# The contents (META's files) of this tarball comes from findlib
# This tarball have to be updated when findlib or ocaml are updated to a new version
# these META's files are only generated by the ./configure in the findlib source directory
# (camlp4 and ocaml-labltk have to be installed for this operation)
# then just:
# tar cfj  findlib-1.2.6-ocaml-3.11.2-meta-files.tar.bz2  site-lib-src/*/META
Source5:	findlib-1.2.6-ocaml-3.11.2-meta-files.tar.bz2

Patch0:         ocaml-3.12.0-rpath.patch
Patch1:         ocaml-user-cflags.patch
Patch3:		ocaml-3.11.0-ocamltags-no-site-start.patch
Patch6:		ocaml-3.04-do-not-add-rpath-X11R6_lib-when-using-option-L.patch
Patch7:		ocaml-3.11.0-no-opt-for-debug-and-profile.patch
Patch8:		ocaml-3.04-larger-buffer-for-uncaught-exception-messages.patch
Patch9:		ocaml-3.12.0-handle-tk-8.6.patch
Patch16:	ocaml-3.09.2-lib64.patch
Patch17:	ocaml-3.11.0-db4.patch
Patch18:	ocaml-3.09.3-compile-emacs-files-in-build-dir.patch

BuildRequires:	libx11-devel
BuildRequires:	ncurses-devel
BuildRequires:	tcl
BuildRequires:	tcl-devel
BuildRequires:	tk
BuildRequires:	tk-devel
BuildRequires:	emacs
BuildRequires:	db5.1-devel

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
%patch0 -p1 -b .rpath
%patch1 -p1 -b .cflags
%patch3 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1 -b .tk
%patch16 -p1 -b .lib64
%patch17 -p1 -b .db4
#patch18 -p1 -b .emacs

rm -rf `find -name .cvsignore`

# fix incorrect reference in camlp4 META file
perl -pi -e 's|/usr/lib/ocaml/camlp4|%{_libdir}/ocaml/camlp4|' \
    site-lib-src/camlp4/META

%build
%ifarch alpha
echo %{optflags} | grep -q mieee || { echo "on alpha you need -mieee to compile ocaml"; exit 1; }
%endif

CFLAGS="$RPM_OPT_FLAGS" ./configure \
    -bindir %{_bindir} \
    -libdir %{_libdir}/ocaml \
    -x11lib %{_libdir} \
    -x11include %{_includedir} \
    -mandir %{_mandir}/man1

make world
%if %{build_ocamlopt}
make opt opt.opt
%endif
make -C emacs ocamltags


%install
rm -rf %{buildroot}
make install BINDIR=%{buildroot}%{_bindir} LIBDIR=%{buildroot}%{_libdir}/ocaml MANDIR=%{buildroot}%{_mandir}

# remove stupid camlp4o.opt which can't work
#rm -f %{buildroot}%{_bindir}/camlp4*.opt
#rm -f %{buildroot}%{_mandir}/man1/camlp4*.opt.*

cd emacs; make install install-ocamltags BINDIR=%{buildroot}%{_bindir} EMACSDIR=%{buildroot}%{_datadir}/emacs/site-lisp; cd -

# fix
perl -pi -e "s|%{buildroot}||" %{buildroot}%{_libdir}/ocaml/ld.conf

%if %{build_ocamlopt}
# only keep the binary versions, which are much faster, except for camlp4
# as native code cannot do a dynamic load
for i in %{buildroot}%{_bindir}/*.opt ; do
  [[ $i == %{buildroot}%{_bindir}/camlp4* ]] && continue
  ln -sf `basename $i` ${i%.opt}
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

# install findlib META files
cp -pr site-lib-src/* %{buildroot}%{_libdir}/ocaml/

rm -f %{name}.list
n="labltk|camlp4|ocamlbrowser|tkanim"
(cd %{buildroot} ; find usr/bin ! -type d -printf "/%%p\n" | egrep -v $n) >> %{name}.list
(cd %{buildroot} ; find usr/%{_lib}/ocaml ! -type d -printf "/%%p\n" | egrep -v $n) >> %{name}.list
(cd %{buildroot} ; find usr/%{_lib}/ocaml   -type d -printf "%%%%dir /%%p\n" | egrep -v $n) >> %{name}.list

# install sources
install -d -m 755 %{buildroot}%{_prefix}/src
tar xvjf %{SOURCE0} -C %{buildroot}%{_prefix}/src
mv %{buildroot}%{_prefix}/src/%{name}-%{version} %{buildroot}%{_prefix}/src/%{name}
install -d %{buildroot}%{_includedir}
ln -s %{_libdir}/ocaml/caml %{buildroot}%{_includedir}/

%clean
rm -rf %{buildroot}

%files -f %{name}.list
%defattr(-,root,root)
%doc Changes LICENSE README
%{_includedir}/caml
%{_mandir}/man1/*
%{_datadir}/emacs/site-lisp/*
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*

%files doc
%defattr(-,root,root)
%doc htmlman/* 
%if %build_ocamlopt
%{_mandir}/man3/*
%endif

%if %{build_labltk}
%files labltk
%defattr(-,root,root)
%doc otherlibs/labltk/README otherlibs/labltk/example*
%{_bindir}/*labltk*
%{_bindir}/ocamlbrowser
%{_libdir}/ocaml/*labltk*
%{_libdir}/ocaml/stublibs/dlllabltk.so
%endif

%files -n camlp4
%defattr(-,root,root)
%{_bindir}/*camlp4*
%{_libdir}/ocaml/camlp4

%files sources
%defattr(-,root,root)
%{_prefix}/src/%{name}
