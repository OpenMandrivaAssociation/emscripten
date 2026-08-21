%undefine _debugsource_packages

Name:		emscripten
Version:	6.0.8
Release:	1
Source0:	https://github.com/emscripten-core/emscripten/archive/%{version}/%{name}-%{version}.tar.gz
# Vendored npm production modules (acorn, html-minifier-terser, closure compiler).
# Built offline from package-lock.json. Closure uses the bundled Java compiler
# when --closure is requested (optional; needs a JRE).
Source1:	emscripten-%{version}-node_modules.tar.gz
Patch0:		emscripten-6.0.8-clang23-prio-ctor-dtor.patch
Summary:	Compiler that compiles C and C++ to WebAssembly
URL:		https://emscripten.org/
License:	MIT AND NCSA
Group:		Development/Tools
BuildArch:	noarch

BuildRequires:	python

Requires:	python
Requires:	nodejs
Requires:	binaryen
Requires:	clang
Requires:	llvm
Requires:	lld
# Huge file tree; skip automatic ELF/GIR scanners (deps are listed above)
AutoReq:	no
AutoProv:	no

%description
Emscripten is a complete compiler toolchain to WebAssembly, using LLVM, with
a special focus on speed, size, and the Web platform.

This package uses the system LLVM, Binaryen, and Node.js. The first compile
populates ~/.cache/emscripten with libc and compiler-rt.

%prep
%autosetup -p1
# Official tags still ship the in-tree -git suffix
sed -i -e 's/^%{version}-git$/%{version}/' emscripten-version.txt
# install.py always tries npm (no network during the build)
sed -i -e '/^  npm_install(target)/s/.*/  pass/' tools/install.py
# Avoid a hardcoded /usr/local python
sed -i -e 's,/usr/local/bin/python,%{_bindir}/python,g' \
	third_party/ply/doc/makedoc.py third_party/ply/example/yply/yply.py
# Prefer `python` over `python3` in the generated launchers
sed -i -e 's/command -v python3/command -v python/' \
	tools/maint/run_python.sh tools/maint/run_python_compiler.sh
# Generate the emcc/em++/... launchers that the in-tree cache builder execs
python tools/maint/create_entry_points.py

%install
python tools/install.py %{buildroot}%{_prefix}/lib/emscripten

tar -xf %{SOURCE1} -C %{buildroot}%{_prefix}/lib/emscripten

cat >%{buildroot}%{_prefix}/lib/emscripten/.emscripten <<EOF
import os
NODE_JS = '%{_bindir}/node'
LLVM_ROOT = '%{_bindir}'
BINARYEN_ROOT = '%{_prefix}'
EMSCRIPTEN_ROOT = '%{_prefix}/lib/emscripten'
CACHE = os.path.expanduser('~/.cache/emscripten')
EOF

# PATH-friendly wrappers around the Python entry points
mkdir -p %{buildroot}%{_bindir}
for i in em++ em-config emar embuilder emcc emcmake emconfigure emmake \
		emranlib emrun emscons emsize emstrip emscan-deps; do
	cat >%{buildroot}%{_bindir}/$i <<EOF
#!/bin/sh
exec python -E %{_prefix}/lib/emscripten/$i.py "\$@"
EOF
	chmod +x %{buildroot}%{_bindir}/$i
done
for i in emsymbolizer emprofile emdwp emnm empath-split; do
	cat >%{buildroot}%{_bindir}/$i <<EOF
#!/bin/sh
exec python -E %{_prefix}/lib/emscripten/tools/$i.py "\$@"
EOF
	chmod +x %{buildroot}%{_bindir}/$i
done

# npm can leave odd ownership/modes
find %{buildroot}%{_prefix}/lib/emscripten -type d -exec chmod 755 {} +
find %{buildroot}%{_prefix}/lib/emscripten -type f -exec chmod a+r {} +

%files
%{_bindir}/*
%{_prefix}/lib/emscripten
