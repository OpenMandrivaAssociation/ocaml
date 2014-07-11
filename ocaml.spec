%define build_ocamlopt	1
%ifarch ppc64 %mips
%define build_ocamlopt	0
%endif
%define build_labltk	1
%define major	4.01
%define minor	0

%bcond_with emacs

Summary:	The Objective Caml compiler and programming environment
Name:		ocaml
Version:	%{major}.%{minor}
Release:	9
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
#Patch16:	ocaml-4.00.0-lib64.patch
#Patch18:	ocaml-3.09.3-compile-emacs-files-in-build-dir.patch
# Workaround for upstream http://caml.inria.fr/mantis/view.php?id=5753
# Remove ocamltoplevel.cmxa from META file
Patch19:	ocaml-4.00.1-fix-META-ocamltoplevel.cmxa.patch

#fedora patches
Patch100:	0001-Add-.gitignore-file-to-ignore-generated-files.patch
Patch101:	0002-Ensure-empty-compilerlibs-directory-is-created-by-gi.patch
Patch102:	0003-ocamlbyteinfo-ocamlplugininfo-Useful-utilities-from-.patch
Patch103:	0006-Add-support-for-ppc64.patch
Patch104:	0007-yacc-Use-mkstemp-instead-of-mktemp.patch
Patch105:	ocaml-aarch64.patch	

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
Requires: camlp4 = %{EVRD}

%description
Objective Caml is a high-level, strongly-typed, functional and object-oriented
programming language from the ML family of languages.

This package comprises two batch compilers (a fast bytecode compiler and an
optimizing native-code compiler), an interactive toplevel system, Lex&Yacc
tools, a replay debugger, and a comprehensive library.

%package	compiler
Summary:	Compiler and Runtime for OCaml
Group:		Development/Other
Requires:	%{name}-compiler = %{version}
Conflicts:	ocaml < 4.01.0-5

%package	doc
Summary:	Documentation for OCaml
Group:		Development/Other
BuildArch:	noarch
Requires:	%{name}-compiler = %{version}

%package -n	camlp4
Summary:	Preprocessor for OCaml
Group:		Development/Other
Requires:	%{name}-compiler = %{version}

%if %{build_ocamlopt}
%package -n	camlp4-devel
Summary:	Development files for camlp4
Group:		Development/Other
Requires:	camlp4 = %{version}
Requires:	%{name}-compiler = %{version}
%endif

%package labltk
Summary:	Tk toolkit binding for OCaml
Group:		Development/Other
Requires:	%{name}-compiler = %{version}
Requires:	tk-devel
Obsoletes:	ocamltk < %{version}
%define	__noautoreq '(/usr/bin/ocamlrun)'

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

%description -n	camlp4
Preprocessor for OCaml

%if %{build_ocamlopt}
%description -n	camlp4-devel
This package contains the development files needed to build applications
using camlp4.
%endif

%description labltk
Tk toolkit binding for OCaml

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
%setup -q -T -D -a 5
%apply_patches
# delete backup files to be sure that they don't end up in package
find -name \*.00??~ -delete
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

%if %{build_ocamlopt}
# only keep the binary versions, which are much faster, except for camlp4
# as native code cannot do a dynamic load
for i in %{buildroot}%{_bindir}/*.opt ; do
  [[ $i == %{buildroot}%{_bindir}/camlp4* ]] && continue
  ln -sf `basename $i` ${i%.opt}
done
%endif

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

# install findlib META files
cp -pr site-lib-src/* %{buildroot}%{_libdir}/ocaml/

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
%dir %{_libdir}/ocaml/camlp4
%dir %{_libdir}/ocaml/camlp4/Camlp4Filters
%dir %{_libdir}/ocaml/camlp4/Camlp4Parsers
%dir %{_libdir}/ocaml/camlp4/Camlp4Printers
%dir %{_libdir}/ocaml/camlp4/Camlp4Top
%{_libdir}/ocaml/camlp4/META
%{_libdir}/ocaml/camlp4/*.cma
%{_libdir}/ocaml/camlp4/*.cmi
%{_libdir}/ocaml/camlp4/*.cmo
%{_libdir}/ocaml/camlp4/*/*.cmi
%{_libdir}/ocaml/camlp4/*/*.cmo

%if %{build_ocamlopt}
%files -n camlp4-devel
%{_libdir}/ocaml/camlp4/*.a
%{_libdir}/ocaml/camlp4/*.o
%{_libdir}/ocaml/camlp4/*.cmxa
%{_libdir}/ocaml/camlp4/*.cmx
%{_libdir}/ocaml/camlp4/*/*.o
%{_libdir}/ocaml/camlp4/*/*.cmx
%endif

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
%{_libdir}/ocaml/graphics/META
%dir %{_libdir}/ocaml/graphics
%{_libdir}/ocaml/graphicsX11.cmi
%if %{build_ocamlopt}
%{_libdir}/ocaml/graphicsX11.cmx
%endif
%{_libdir}/ocaml/graphicsX11.mli

%files sources
%{_prefix}/src/%{name}

%files compiler-libs
%dir %{_libdir}/ocaml/compiler-libs
%{_libdir}/ocaml/compiler-libs/META
%{_libdir}/ocaml/compiler-libs/*.cmi
%{_libdir}/ocaml/compiler-libs/*.cmo
%{_libdir}/ocaml/compiler-libs/*.cma
%if %{build_ocamlopt}
%{_libdir}/ocaml/compiler-libs/*.a
%{_libdir}/ocaml/compiler-libs/*.cmxa
/%{_libdir}/ocaml/compiler-libs/*.cmx
%{_libdir}/ocaml/compiler-libs/*.o
%endif
