%undefine _debugsource_packages

Name: emscripten
Version: 3.1.73
Release: 1
Source0: https://github.com/emscripten-core/emscripten/archive/%{version}/%{name}-%{version}.tar.gz
Summary: Compiler that compiles C and C++ to WebAssembly
URL: https://emscripten.org/
License: MIT, University of Illinois/NCSA Open Source License
Group: Development/Tools
BuildRequires: make
BuildRequires: binaryen
BuildRequires: nodejs

%description
Emscripten is a complete compiler toolchain to WebAssembly, using LLVM, with
a special focus on speed, size, and the Web platform.

%prep
%autosetup -p1
sed -i -e 's,/usr/local/bin/python,%{_bindir}/python,g' third_party/ply/doc/makedoc.py third_party/ply/example/yply/yply.py

%install
%make_install DESTDIR="%{buildroot}%{_prefix}/lib/emscripten"

# Let's use some slightly less weird wrappers and make them $PATH friendly...
mkdir -p %{buildroot}%{_bindir}
for i in em++ em-config emar embuilder emcc emcmake emconfigure emmake emranlib emrun emscon emsize emstrip emsymbolizer; do
	cat >%{buildroot}%{_bindir}/$i <<EOF
#!/bin/sh
exec python -E %{_prefix}/lib/emscripten/$i.py "\$@"
EOF
	chmod +x %{buildroot}%{_bindir}/$i
done

%files
%{_bindir}/*
%{_prefix}/lib/emscripten
