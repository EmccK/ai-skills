```rust
mod api;
mod models;
mod services;

use std::{env, path::PathBuf};

use api::router as api_router;
use axum::Router;
use tokio::net::TcpListener;
use tower_http::services::{ServeDir, ServeFile};

const DEFAULT_PORT: u16 = {PORT};

#[tokio::main]
async fn main() {
    let port = env::var("PORT")
        .map(|value| value.parse::<u16>().expect("PORT 必须是合法的端口号"))
        .unwrap_or(DEFAULT_PORT);

    let dist_dir = frontend_dist_dir();
    let index_file = dist_dir.join("index.html");

    // API 路由和前端静态资源分开，避免 /api/* 被 SPA 回退吞掉
    let spa_service = ServeDir::new(dist_dir).fallback(ServeFile::new(index_file));

    let app = Router::new()
        .nest("/api", api_router())
        .fallback_service(spa_service);

    let listener = TcpListener::bind(("0.0.0.0", port))
        .await
        .expect("监听端口失败");

    println!("server running at http://0.0.0.0:{port}");

    axum::serve(listener, app).await.expect("启动服务失败");
}

fn frontend_dist_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("frontend")
        .join("dist")
}
```
