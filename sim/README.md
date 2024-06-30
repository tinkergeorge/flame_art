# Light Curve Simulator

## Building & running instructions (all platforms):

Follow the steps [here](https://www.rust-lang.org/learn/get-started) to get the Rust toolchain installed. Verify that it's installed by doing `cargo --version`.

To build and run the program, just:

```
cd sim
cargo run
```

This will download all dependencies, compile, and run the simulator.
Future runs of `cargo run` should be much faster.

If it runs slowly, use `cargo run --release` instead of `cargo run` to do a release build. Build will be slightly slower and it will be missing debug symbols but it should run faster.
