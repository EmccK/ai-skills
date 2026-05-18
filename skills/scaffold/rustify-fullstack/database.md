## 数据库支持

三种模式：
1. **不需要** — 不添加数据库依赖
2. **单选** — 只用一种数据库
3. **多数据库切换** — Cargo features 编译时选择，指定默认

支持的数据库：SQLite、PostgreSQL、MySQL

统一使用 sqlx 作为数据库抽象层。

## Cargo.toml — 单选模式

SQLite：
```toml
[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio", "sqlite"] }
```

PostgreSQL：
```toml
[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres"] }
```

MySQL：
```toml
[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio", "mysql"] }
```

## Cargo.toml — 多数据库切换模式

通过 Cargo features 控制编译哪个后端，指定一个 default：

```toml
[features]
default = ["sqlite"]
sqlite = ["sqlx/sqlite"]
postgres = ["sqlx/postgres"]
mysql = ["sqlx/mysql"]

[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio"] }
```

编译时切换：
```bash
# 使用默认（SQLite）
cargo build

# 切换到 PostgreSQL
cargo build --no-default-features --features postgres

# 切换到 MySQL
cargo build --no-default-features --features mysql
```

## src/db.rs — 数据库连接模块

```rust
use sqlx::Pool;

#[cfg(feature = "sqlite")]
pub type Db = sqlx::Sqlite;

#[cfg(feature = "postgres")]
pub type Db = sqlx::Postgres;

#[cfg(feature = "mysql")]
pub type Db = sqlx::MySql;

pub type DbPool = Pool<Db>;

pub async fn connect(url: &str) -> DbPool {
    Pool::<Db>::connect(url)
        .await
        .expect("数据库连接失败")
}
```

## src/main.rs 中集成数据库

在 main 函数中初始化连接池，通过 axum State 共享：

```rust
mod db;

use db::{DbPool, connect};

#[tokio::main]
async fn main() {
    let database_url = env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite:data.db?mode=rwc".to_string());

    let pool: DbPool = connect(&database_url).await;

    let app = Router::new()
        .nest("/api", api_router())
        .fallback_service(spa_service)
        .with_state(pool);

    // ...
}
```

## 环境变量

```bash
# SQLite
DATABASE_URL=sqlite:data.db?mode=rwc

# PostgreSQL
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# MySQL
DATABASE_URL=mysql://user:pass@localhost:3306/dbname
```

## compose.yml 补充（按需添加）

PostgreSQL：
```yaml
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER:-app}
      POSTGRES_PASSWORD: ${DB_PASS:-app}
      POSTGRES_DB: ${DB_NAME:-app}
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

MySQL：
```yaml
services:
  db:
    image: mysql:9
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASS:-root}
      MYSQL_USER: ${DB_USER:-app}
      MYSQL_PASSWORD: ${DB_PASS:-app}
      MYSQL_DATABASE: ${DB_NAME:-app}
    volumes:
      - mysqldata:/var/lib/mysql

volumes:
  mysqldata:
```

## 目录结构变化

选择数据库后，增加：
```
src/
├── db.rs          # 连接池与类型别名
├── models/
│   └── mod.rs     # 数据模型（sqlx::FromRow）
```
