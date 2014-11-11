%define build_ocamlopt	1
%define build_labltk	1
%define major	4.02
%define minor	1

%bcond_with emacs

Summary:	The Objective Caml compiler and programming environment
Name:		ocaml
Version:	%{major}.%{minor}
Release:	10
License:	QPL with exceptions and LGPLv2 with exceptions
Group:		Development/Other
Url:		http://caml.inria.fr
Source0:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{version}.tar.gz
Source1:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{major}-refman-html.tar.gz
Source3:	ocaml.rpmlintrc

Patch0:		ocaml-3.11.0-ocamltags-no-site-start.patch
Patch1:		ocaml-3.11.0-no-opt-for-debug-and-profile.patch
Patch2:		ocaml-3.04-larger-buffer-for-uncaught-exception-messages.patch
Patch4:		0005-configure-Allow-user-defined-C-compiler-flags.patch

# fedora
Patch1001:      0001-Don-t-ignore-.-configure-it-s-a-real-git-file.patch
Patch1002:      0002-Ensure-empty-compilerlibs-directory-is-created-by-gi.patch
Patch1003:      0003-Don-t-add-rpaths-to-libraries.patch
Patch1004:      0004-ocamlbyteinfo-ocamlplugininfo-Useful-utilities-from-.patch
Patch1006:      0006-Add-support-for-ppc64.patch
Patch1007:      0007-ppc64-Update-for-OCaml-4.02.0.patch
Patch1008:      0008-Add-support-for-ppc64le.patch
Patch1009:      0009-ppc64le-Update-for-OCaml-4.02.0.patch
Patch1010:      0010-arm-arm64-Mark-stack-as-non-executable.patch
Patch1011:      0011-arg-Add-no_arg-and-get_arg-helper-functions.patch
Patch1012:      0012-arg-Allow-flags-such-as-flag-arg-as-well-as-flag-arg.patch
Patch1013:      0013-PR-6517-use-ISO-C99-types-u-int-32-64-_t-in-preferen.patch
Patch1014:      0014-ppc-ppc64-ppc64le-Mark-stack-as-non-executable.patch
Patch1015:      0015-ppc64-ppc64le-proc-Interim-definitions-for-op_is_pur.patch

BuildRequires:	db-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(tcl)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(tk)
%if %{with emacs}
BuildRequires:	emacs
%rename		ocaml-emacs
%endif

Requires: %{name}-compiler = %{EVRD}
Requires: %{name}-compiler-libs = %{EVRD}

%description
Objective Caml is a high-level, strongly-typed, functional and object-oriented
programming language from the ML family of languages.

This package comprises two batch compilers (a fast bytecode compiler and an
optimizing native-code compiler), an interactive toplevel system, Lex&Yacc
tools, a replay debugger, and a comprehensive library.

%package	compiler
Summary:	Compiler and Runtime for OCaml
Group:		Development/Other
Provides:	%{_bindir}/ocamlrun %{version}
Requires:	%{name}-compiler = %{version}
Conflicts:	ocaml < 4.01.0-5

%package	doc
Summary:	Documentation for OCaml
Group:		Development/Other
BuildArch:	noarch
Requires:	%{name}-compiler = %{version}

%package x11
Summary:	X11 library for OCaml
Group:		Development/Other
Requires:	%{name}-compiler = %{version}
Requires:	pkgconfig(x11)
# 2012-07-14: conflict for upgrade (when the x11 subpackage is created)
Conflicts:	ocaml < 4.01.0-5

%package sources
Summary:	OCaml sources
Group:		Development/Other
BuildArch:	noarch
# don't add crazy deps
AutoReqProv: No

%package compiler-libs
Summary:	OCaml compiler library
Group:		Development/Other
Requires:	%{name}-compiler = %{version}
Conflicts:	%{name} < 4.01.0-5

%description
OCaml is a high-level, strongly-typed, functional and object-oriented
programming language from the ML family of languages.

%description compiler
This package comprises two batch OCaml compilers (a fast byte-code compiler and
an optimizing native-code compiler), an interactive top-level system, Lex&Yacc
tools, a replay debugger, and a comprehensive library.

%description	doc
Documentation for OCaml

%description x11
X11 library for OCaml.

%description sources
OCaml sources

%description compiler-libs
This package contains several modules used internally by the OCaml
compilers.  They are not needed for normal OCaml development, but may
be helpful in the development of certain applications.

%prep
%setup -q -T -b 0
%setup -q -T -D -a 1
%apply_patches
# delete backup files to be sure that they don't end up in package
find -name \*.00??~ -delete
rm -rf `find -name .cvsignore`

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

%if %{with emacs}
cd emacs; make install install-ocamltags \
	BINDIR=%{buildroot}%{_bindir} \
	EMACSDIR=%{buildroot}%{_datadir}/emacs/site-lisp; cd -
%else
make -C emacs install-ocamltags \
	BINDIR=%{buildroot}%{_bindir}
%endif

# fix
perl -pi -e "s|%{buildroot}||" %{buildroot}%{_libdir}/ocaml/ld.conf

%if %{with emacs}
install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(require 'caml-font)
(autoload 'caml-mode "caml" "Caml editing mode" t)
(add-to-list 'auto-mode-alist '("\\\\.mli?$" . caml-mode))
EOF
%endif

# don't package mano man pages since we have the html files
rm -rf %{buildroot}%{_mandir}/mano

# fix me: this one should not be in the input
if [ -f %{buildroot}%{_libdir}/ocaml/dbm/META ]
then rm -f %{buildroot}%{_libdir}/ocaml/dbm/META; fi

rm -f %{name}.list
n="labltk|camlp4|ocamlbrowser|tkanim|graphics|X11"
(cd %{buildroot} ; find usr/bin ! -type d -printf "/%%p\n" | egrep -v $n) >> %{name}.list
(cd %{buildroot} ; find usr/%{_lib}/ocaml ! -type d -printf "/%%p\n" | egrep -v $n) >> %{name}.list
(cd %{buildroot} ; find usr/%{_lib}/ocaml   -type d -printf "%%%%dir /%%p\n" | egrep -v $n) >> %{name}.list

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=OCaml
Comment=%{summary}
Exec=%{name}
Icon=interpreters_section
Terminal=true
Type=Application
Categories=Development;
EOF

# install sources
install -d -m 755 %{buildroot}%{_prefix}/src
tar xvjf %{SOURCE0} -C %{buildroot}%{_prefix}/src
mv %{buildroot}%{_prefix}/src/%{name}-%{version} %{buildroot}%{_prefix}/src/%{name}
install -d %{buildroot}%{_includedir}
ln -s %{_libdir}/ocaml/caml %{buildroot}%{_includedir}/

%files

%files compiler -f %{name}.list
%doc Changes LICENSE README
%{_includedir}/caml
%{_mandir}/man1/*
%{_datadir}/applications/*
%if %{with emacs}
%{_datadir}/emacs/site-lisp/*
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*
%endif
%exclude %{_libdir}/ocaml/compiler-libs

%files doc
%doc htmlman/* 
%{_mandir}/man3/*

%files x11
%if %{build_ocamlopt}
%{_libdir}/ocaml/graphics.a
%endif
%{_libdir}/ocaml/graphics.cma
%{_libdir}/ocaml/graphics.cmi
%if %{build_ocamlopt}
%{_libdir}/ocaml/graphics.cmx
%{_libdir}/ocaml/graphics.cmxa
%{_libdir}/ocaml/graphics.cmxs
%endif
%{_libdir}/ocaml/graphics.mli
%{_libdir}/ocaml/libgraphics.a
%{_libdir}/ocaml/stublibs/dllgraphics.so
#% dir %{_libdir}/ocaml/graphics
%{_libdir}/ocaml/graphicsX11.cmi
%if %{build_ocamlopt}
%{_libdir}/ocaml/graphicsX11.cmx
%endif
%{_libdir}/ocaml/graphicsX11.mli

%files sources
%{_prefix}/src/%{name}

%files compiler-libs
%dir %{_libdir}/ocaml/compiler-libs
%{_libdir}/ocaml/compiler-libs/*.cmi
%{_libdir}/ocaml/compiler-libs/*.cmo
%{_libdir}/ocaml/compiler-libs/*.cma
%if %{build_ocamlopt}
%{_libdir}/ocaml/compiler-libs/*.a
%{_libdir}/ocaml/compiler-libs/*.cmxa
/%{_libdir}/ocaml/compiler-libs/*.cmx
%{_libdir}/ocaml/compiler-libs/*.o
%endif
