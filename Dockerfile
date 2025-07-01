FROM python:3.12.8-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && apt-get -y install --no-install-recommends \
  autoconf \
  automake \
  build-essential \
  cmake \
  git-core \
  libass-dev \
  libfreetype6-dev \
  libgnutls28-dev \
  libmp3lame-dev \
  libtool \
  libvorbis-dev \
  meson \
  ninja-build \
  pkg-config \
  texinfo \
  wget \
  yasm \
  zlib1g-dev \
  nasm \
  libunistring-dev \
  libnuma-dev \
  ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* && \
  #Create directories
  mkdir -p ~/ffmpeg_sources ~/bin && \
  #Install libx264
  cd ~/ffmpeg_sources && \
  git -C x264 pull 2> /dev/null || git clone --depth 1 https://code.videolan.org/videolan/x264.git && \
  cd x264 && \
  PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --enable-static --enable-pic && \
  PATH="$HOME/bin:$PATH" make -j$(nproc) && \
  make install && \
  #Install libx265
  cd ~/ffmpeg_sources && \
  wget -O x265.tar.bz2 https://bitbucket.org/multicoreware/x265_git/get/master.tar.bz2 && \
  tar xjvf x265.tar.bz2 && \
  cd multicoreware*/build/linux && \
  PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED=off ../../source && \
  PATH="$HOME/bin:$PATH" make -j$(nproc) && \
  make install && \
  #Install libvpx
  cd ~/ffmpeg_sources && \
  git -C libvpx pull 2> /dev/null || git clone --depth 1 https://chromium.googlesource.com/webm/libvpx.git && \
  cd libvpx && \
  PATH="$HOME/bin:$PATH" ./configure --prefix="$HOME/ffmpeg_build" --disable-examples --disable-unit-tests --enable-vp9-highbitdepth --as=yasm && \
  PATH="$HOME/bin:$PATH" make -j$(nproc) && \
  make install && \
  #Install libfdk-aac
  cd ~/ffmpeg_sources && \
  git -C fdk-aac pull 2> /dev/null || git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
  cd fdk-aac && \
  autoreconf -fiv && \
  ./configure --prefix="$HOME/ffmpeg_build" --disable-shared && \
  make -j$(nproc) && \
  make install && \
  #Install libopus
  cd ~/ffmpeg_sources && \
  git -C opus pull 2> /dev/null || git clone --depth 1 https://github.com/xiph/opus.git && \
  cd opus && \
  ./autogen.sh && \
  ./configure --prefix="$HOME/ffmpeg_build" --disable-shared && \
  make -j$(nproc) && \
  make install && \
  #Install libaom
  cd ~/ffmpeg_sources && \
  cd ~/ffmpeg_sources && \
  git -C aom pull 2> /dev/null || git clone --depth 1 https://aomedia.googlesource.com/aom && \
  mkdir -p aom_build && \
  cd aom_build && \
  PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_TESTS=OFF -DENABLE_NASM=on ../aom && \
  PATH="$HOME/bin:$PATH" make -j$(nproc) && \
  make install && \
  #Install libsvtav1
  cd ~/ffmpeg_sources && \
  git -C SVT-AV1 pull 2> /dev/null || git clone https://gitlab.com/AOMediaCodec/SVT-AV1.git && \
  mkdir -p SVT-AV1/build && \
  cd SVT-AV1/build && \
  PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DCMAKE_BUILD_TYPE=Release -DBUILD_DEC=OFF -DBUILD_SHARED_LIBS=OFF .. && \
  PATH="$HOME/bin:$PATH" make -j$(nproc) && \
  make install && \
  #Install libdav1d
  cd ~/ffmpeg_sources && \
  git -C dav1d pull 2> /dev/null || git clone --depth 1 https://code.videolan.org/videolan/dav1d.git && \
  mkdir -p dav1d/build && \
  cd dav1d/build && \
  meson setup -Denable_tools=false -Denable_tests=false --default-library=static .. --prefix "$HOME/ffmpeg_build" --libdir="$HOME/ffmpeg_build/lib" && \
  ninja -j$(nproc) && \
  ninja install && \
  #Install libvmaf
  cd ~/ffmpeg_sources && \
  wget https://github.com/Netflix/vmaf/archive/v3.0.0.tar.gz && \
  tar xvf v3.0.0.tar.gz && \
  mkdir -p vmaf-3.0.0/libvmaf/build &&\
  cd vmaf-3.0.0/libvmaf/build && \
  meson setup -Denable_tests=false -Denable_docs=false --buildtype=release --default-library=static .. --prefix "$HOME/ffmpeg_build" --bindir="$HOME/bin" --libdir="$HOME/ffmpeg_build/lib" && \
  ninja -j$(nproc) && \
  ninja install && \
  #Install FFmpeg
  cd ~/ffmpeg_sources && \
  wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
  tar xjvf ffmpeg-snapshot.tar.bz2 && \
  cd ffmpeg && \
  PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
  --prefix="$HOME/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$HOME/ffmpeg_build/include" \
  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
  --extra-libs="-lpthread -lm" \
  --ld="g++" \
  --bindir="$HOME/bin" \
  --enable-gpl \
  --enable-gnutls \
  --enable-libaom \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libsvtav1 \
  --enable-libdav1d \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree && \
  PATH="$HOME/bin:$PATH" make -j$(nproc) && \
  make install && \
  hash -r && \
  cp ~/bin/ffmpeg /usr/local/bin/ffmpeg && \
  cp ~/bin/ffprobe /usr/local/bin/ffprobe && \
  #Cleanup
  apt-get purge -y \
  autoconf \
  automake \
  build-essential \
  cmake \
  git-core \
  libtool \
  meson \
  ninja-build \
  pkg-config \
  texinfo \
  wget \
  yasm \
  nasm && \
  apt-get autoremove -y && \
  apt-get clean && \
  rm -rf \
  ~/ffmpeg_sources \
  ~/bin \
  ~/ffmpeg_build \
  /var/lib/apt/lists/* \
  /var/cache/apt/archives/*