%define build_ocamlopt	1
%ifarch ppc64 %mips
%define build_ocamlopt	0
%endif
%define build_labltk	1
%define major	4.01
%define minor	0

Summary:	The Objective Caml compiler and programming environment
Name:		ocaml
Version:	%{major}.%{minor}
Release:	1
License:	QPL with exceptions and LGPLv2 with exceptions
Group:		Development/Other
Url:		http://caml.inria.fr
Source0:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{version}.tar.bz2
Source1:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{major}-refman-html.tar.gz
Source3:	ocaml.rpmlintrc

# IMPORTANT:
# The contents (META's files) of this tarball comes from findlib
# This tarball have to be updated when findlib or ocaml are updated to a new version
# these META's files are only generated by the ./configure in the findlib source directory
# (camlp4 and ocaml-labltk have to be installed for this operation)
# steps:
# get findlib sources from http://projects.camlcity.org/projects/findlib.html
# extract, run ./configure
# then,
# tar -Jcf findlib-1.2.7-ocaml-%{version}-meta-files.tar.xz  site-lib-src/*/META
# notice the version macro in filename, this to imply that the META files has
# to be built for *THIS* specific version!
Source5:	findlib-1.3.3-ocaml-4.00.0-meta-files.tar.xz

Patch0:		ocaml-3.12.0-rpath.patch
Patch1:		ocaml-user-cflags.patch
Patch3:		ocaml-3.11.0-ocamltags-no-site-start.patch
Patch7:		ocaml-3.11.0-no-opt-for-debug-and-profile.patch
Patch8:		ocaml-3.04-larger-buffer-for-uncaught-exception-messages.patch
Patch16:	ocaml-4.00.0-lib64.patch
#fedora patches
Patch17:      0001-Add-.gitignore-file-to-ignore-generated-files.patch
Patch18:      0002-Ensure-empty-compilerlibs-directory-is-created-by-gi.patch
Patch19:      0003-ocamlbyteinfo-ocamlplugininfo-Useful-utilities-from-.patch
Patch22:      0006-Add-support-for-ppc64.patch
Patch23:      0007-yacc-Use-mkstemp-instead-of-mktemp.patch
Patch24:	ocaml-aarch64.patch	

BuildRequires:	emacs
BuildRequires:	db-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(tcl)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(tk)
%rename		ocaml-emacs

%description
Objective Caml is a high-level, strongly-typed, functional and object-oriented
programming language from the ML family of languages.

This package comprises two batch compilers (a fast bytecode compiler and an
optimizing native-code compiler), an interactive toplevel system, Lex&Yacc
tools, a replay debugger, and a comprehensive library.

%package	doc
Summary:	Documentation for OCaml
Group:		Books/Computer books
Requires:	%{name} = %{version}

%description	doc
Documentation for OCaml

%package -n	camlp4
Summary:	Preprocessor for OCaml
Group:		Development/Other
Requires:	%{name} = %{version}

%description -n	camlp4
Preprocessor for OCaml

%package	labltk
Summary:	Tk toolkit binding for OCaml
Group:		Development/Other
Requires:	%{name} = %{version}
Requires:	tk-devel

%description	labltk
Tk toolkit binding for OCaml

%package	sources
Summary:	OCaml sources
Group:		Development/Other
# don't add crazy deps
AutoReqProv:	No

%description	sources
OCaml sources

%prep
%setup -q -T -b 0
%setup -q -T -D -a 1
%setup -q -T -D -a 5
%apply_patches
rm -rf `find -name .cvsignore`

# fix incorrect reference in camlp4 META file
sed -ri -e 's|directory = "/usr/lib.*/ocaml/camlp4"|directory = "%{_libdir}/ocaml/camlp4"|g' site-lib-src/camlp4/META

%build
%ifarch alpha
echo %{optflags} | grep -q mieee || { echo "on alpha you need -mieee to compile ocaml"; exit 1; }
%endif

CFLAGS="%optflags" ./configure \
    -bindir %{_bindir} \
    -host %{_host} \
    -cc "%{__cc}" \
    -as "%{__as}" \
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
make install \
	BINDIR=%{buildroot}%{_bindir} \
	LIBDIR=%{buildroot}%{_libdir}/ocaml \
	MANDIR=%{buildroot}%{_mandir}

# remove stupid camlp4o.opt which can't work
#rm -f %{buildroot}%{_bindir}/camlp4*.opt
#rm -f %{buildroot}%{_mandir}/man1/camlp4*.opt.*

cd emacs; make install install-ocamltags \
	BINDIR=%{buildroot}%{_bindir} \
	EMACSDIR=%{buildroot}%{_datadir}/emacs/site-lisp; cd -

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

%files -f %{name}.list
%doc Changes LICENSE README
%{_includedir}/caml
%{_mandir}/man1/*
%{_datadir}/emacs/site-lisp/*
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*

%files doc
%doc htmlman/* 
%if %build_ocamlopt
%{_mandir}/man3/*
%endif

%if %{build_labltk}
%files labltk
%doc otherlibs/labltk/README otherlibs/labltk/example*
%{_bindir}/*labltk*
%{_bindir}/ocamlbrowser
%{_libdir}/ocaml/*labltk*
%{_libdir}/ocaml/stublibs/dlllabltk.so
%endif

%files -n camlp4
%{_bindir}/*camlp4*
%{_libdir}/ocaml/camlp4

%files sources
%{_prefix}/src/%{name}

