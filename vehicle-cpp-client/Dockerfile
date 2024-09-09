FROM archlinux:latest

# Install dependencies
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    base-devel \
    cmake \
    git \
    grpc \
    protobuf \
    && pacman -Scc --noconfirm  # Clean the package cache to reduce image size

# Set working directory
WORKDIR /taskscripts
# Copy your C++ project files
COPY . .
# Run your application
CMD ["./client"]
