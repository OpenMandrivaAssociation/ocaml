%define _disable_ld_no_undefined 1
%define _disable_lto 1
%define build_ocamlopt 1
%define build_labltk 1
%define major 4.07
%define minor 0

# -fomit-frame-pointer and -pg are mutually exclusive (and ocaml adds the latter)
%global optflags %(echo %{optflags} |sed -e 's,-fomit-frame-pointer,,g') -fcommon

%bcond_with emacs
%bcond_with bootstrap

Summary:	The Objective Caml compiler and programming environment
Name:		ocaml
Version:	%{major}.%{minor}
Release:	9
License:	QPL with exceptions and LGPLv2 with exceptions
Group:		Development/Other
Url:		http://ocaml.org/
Source0:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{version}.tar.xz
Source1:	http://caml.inria.fr/pub/distrib/ocaml-%{major}/%{name}-%{major}-refman-html.tar.gz
Source3:	ocaml.rpmlintrc
Source4:	https://src.fedoraproject.org/rpms/ocaml-srpm-macros/raw/master/f/macros.ocaml-srpm

Patch0:		ocaml-3.11.0-ocamltags-no-site-start.patch
Patch2:		ocaml-3.04-larger-buffer-for-uncaught-exception-messages.patch
Patch3:		ocaml-4.07.0-lto.patch
Patch4:		ocaml-4.02.1-respect-cflags-ldflags.patch

# fedora
Patch1000:	https://src.fedoraproject.org/rpms/ocaml/raw/master/f/0001-Don-t-add-rpaths-to-libraries.patch
Patch1001:	https://src.fedoraproject.org/rpms/ocaml/raw/master/f/0002-ocamlbyteinfo-ocamlplugininfo-Useful-utilities-from-.patch
Patch1002:	https://src.fedoraproject.org/rpms/ocaml/raw/master/f/0003-configure-Allow-user-defined-C-compiler-flags.patch
Patch1003:	https://src.fedoraproject.org/rpms/ocaml/raw/master/f/0004-Add-RISC-V-backend.patch
Patch1004:	https://src.fedoraproject.org/rpms/ocaml/raw/master/f/0005-Copyright-untabify.patch
Patch1005:	https://src.fedoraproject.org/rpms/ocaml/raw/master/f/0006-fix-caml_c_call-reload-caml_young_limit.patch

Patch1006:	ocaml-SIGSTKSZ.patch
Patch1007:	ocaml-4.07.0-fix-clang.patch

# Additional RISC-V patches from https://github.com/nojb/riscv-ocaml
Patch1500:	https://github.com/nojb/riscv-ocaml/commit/20b4961970d4d5bcef4fc9f449dd7ad9ebc11d66.patch

BuildRequires:	db-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(tcl)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(tk)
%if %{with emacs}
BuildRequires:	emacs
%rename		ocaml-emacs
%endif

%if ! %{with bootstrap}
# Not actually used during the build process, but ocamlobjinfo
# is needed to generate the right Provides: automatically.
# Without the build dependency (fine while bootstrapping), the
# varioud ocaml(Stdlib_*) provides etc. will be missing
# (but the requirements will still be generated by things trying
# to use ocaml...)
BuildRequires:	%{name}-compiler
%endif

Requires:	%{name}-compiler = %{EVRD}
Requires:	%{name}-compiler-libs = %{EVRD}

%description
OCaml is a high-level, strongly-typed, functional and object-oriented
programming language from the ML family of languages.

%package compiler
Summary:	Compiler and Runtime for OCaml
Group:		Development/Other
Provides:	%{_bindir}/ocamlrun %{version}
Requires:	%{name}-compiler = %{version}
Conflicts:	ocaml < 4.01.0-5
# FIXME this is an EVIL workaround for the dependency generator
# getting things wrong
Provides:	ocaml(runtime) = 4.06.0

%description compiler
This package comprises two batch OCaml compilers (a fast byte-code compiler and
an optimizing native-code compiler), an interactive top-level system, Lex&Yacc
tools, a replay debugger, and a comprehensive library.

%package doc
Summary:	Documentation for OCaml
Group:		Development/Other
BuildArch:	noarch
Requires:	%{name}-compiler = %{version}

%description doc
Documentation for OCaml.

%package x11
Summary:	X11 library for OCaml
Group:		Development/Other
Requires:	%{name}-compiler = %{version}
Requires:	pkgconfig(x11)
# 2012-07-14: conflict for upgrade (when the x11 subpackage is created)
Conflicts:	ocaml < 4.01.0-5

%description x11
X11 library for OCaml.

%package sources
Summary:	OCaml sources
Group:		Development/Other
BuildArch:	noarch

%description sources
OCaml sources.

%package compiler-libs
Summary:	OCaml compiler library
Group:		Development/Other
Requires:	%{name}-compiler = %{version}
Conflicts:	%{name} < 4.01.0-5
Provides:	ocaml(runtime) = 4.07.0

%description compiler-libs
This package contains several modules used internally by the OCaml
compilers.  They are not needed for normal OCaml development, but may
be helpful in the development of certain applications.

%prep
%autosetup -p1 -T -b 0

# Fix a couple of bogus paths in scripts that
# get packaged
sed -i -e 's,/usr/local/bin/perl,%{__perl},g' \
	manual/tools/htmlcut \
	manual/tools/texexpand \
	manual/tools/htmltbl \
	manual/tools/htmlthread
sed -i -e 's,/usr/bin/cat,/bin/cat,g' \
	config/auto-aux/hashbang2

# Make sure config/gnu/config.sub knows what a
# riscv64-openmandriva-linux-gnu target is
%config_update

# delete backup files to be sure that they don't end up in package
find -name \*.*~ -delete
rm -rf `find -name .cvsignore`

# Package sources now so the -sources package
# gets all our patches (but not any built
# binaries or refman bits)
cd ..
tar cf sources.tar %{name}-%{version}
mv sources.tar %{name}-%{version}/
cd -

%setup -q -T -D -a 1

%build
%set_build_flags
%ifarch alpha
echo %{optflags} | grep -q mieee || { echo "on alpha you need -mieee to compile ocaml"; exit 1; }
%endif

CFLAGS="%{optflags}" LDFLAGS="%{ldflags}" ./configure \
    -bindir %{_bindir} \
    -host %{_target_platform} \
    -cc "%{__cc}" \
    -as "%{__as}" \
    -libdir %{_libdir}/ocaml \
    -x11lib %{_libdir} \
    -x11include %{_includedir} \
    -mandir %{_mandir}/man1

make world.opt
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
tar xvf sources.tar -C %{buildroot}%{_prefix}/src
mv %{buildroot}%{_prefix}/src/%{name}-%{version} %{buildroot}%{_prefix}/src/%{name}
install -d %{buildroot}%{_includedir}
ln -s %{_libdir}/ocaml/caml %{buildroot}%{_includedir}/

# Fix bogus executable permissions
find %{buildroot} -name "*.ml" |xargs chmod 0644

# We copy the Fedora macros file for compatibility, but then we add our own
# (more useful) set of macros...
install -D -m 644 %{S:4} %{buildroot}%{_prefix}/lib/rpm/macros.d/macros.ocaml
cat >>%{buildroot}%{_prefix}/lib/rpm/macros.d/macros.ocaml <<EOF

%%ocaml_sitelib %%(if [ -x /usr/bin/ocamlc ]; then ocamlc -where;fi)/site-lib
EOF

%files

%files compiler -f %{name}.list
%doc Changes LICENSE
%{_includedir}/caml
%doc %{_mandir}/man1/*
%{_datadir}/applications/*
%if %{with emacs}
%{_datadir}/emacs/site-lisp/*
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*
%endif
%exclude %{_libdir}/ocaml/compiler-libs
%{_prefix}/lib/rpm/macros.d/macros.ocaml

%files doc
%doc htmlman/* 
%{_mandir}/man3/*

%files x11
%if %{build_ocamlopt}
%{_libdir}/ocaml/graphics.a
%endif
%{_libdir}/ocaml/graphics.cma
%{_libdir}/ocaml/graphics.cmi
%{_libdir}/ocaml/graphics.cmti
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
%{_libdir}/ocaml/graphicsX11.cmti
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
%{_libdir}/ocaml/compiler-libs/*.cmt
%{_libdir}/ocaml/compiler-libs/*.cmti
%{_libdir}/ocaml/compiler-libs/*.mli
%if %{build_ocamlopt}
%{_libdir}/ocaml/compiler-libs/*.a
%{_libdir}/ocaml/compiler-libs/*.cmxa
/%{_libdir}/ocaml/compiler-libs/*.cmx
%{_libdir}/ocaml/compiler-libs/*.o
%endif
