```rust
use std::{
    env,
    path::PathBuf,
    process::{Command, Stdio},
};

fn main() {
    // 只有前端源码或依赖声明变化时才重新执行
    println!("cargo:rerun-if-changed=frontend/src");
    println!("cargo:rerun-if-changed=frontend/package.json");
    println!("cargo:rerun-if-changed=frontend/package-lock.json");

    let manifest_dir =
        PathBuf::from(env::var("CARGO_MANIFEST_DIR").expect("缺少 CARGO_MANIFEST_DIR 环境变量"));
    let frontend_dir = manifest_dir.join("frontend");

    if !frontend_dir.exists() {
        panic!("前端目录不存在: {}", frontend_dir.display());
    }

    // CI 用 lockfile 固定依赖；缺少 lockfile 时保留本地开发兼容性
    let install_args = if frontend_dir.join("package-lock.json").exists() {
        ["ci"].as_slice()
    } else {
        ["install"].as_slice()
    };

    run_npm_command(&frontend_dir, install_args);
    run_npm_command(&frontend_dir, &["run", "build"]);
}

fn run_npm_command(frontend_dir: &PathBuf, args: &[&str]) {
    let npm = if cfg!(target_os = "windows") {
        "npm.cmd"
    } else {
        "npm"
    };

    let status = Command::new(npm)
        .args(args)
        .current_dir(frontend_dir)
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .status()
        .unwrap_or_else(|error| panic!("执行命令失败: {} {}，错误: {error}", npm, args.join(" ")));

    if !status.success() {
        panic!("命令执行失败: {} {}", npm, args.join(" "));
    }
}
```
