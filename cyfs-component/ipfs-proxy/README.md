# ipfs-proxy

Support for access to ipfs:// ipns:// links

The underlying layer uses [ipfs kubo](https://github.com/ipfs/kubo), and you need to put the [binary](https://dist.ipfs.tech/#kubo) for the corresponding platform in the same directory as ipfs-proxy.

## How to build

1. Install [Rust](https://www.rust-lang.org/)
2. Run `cargo build -p ipfs-proxy`

## How to use

Place the compiled binary in the %appdata%/cyfs/services/runtime directory and run your browser.