mod ipfs_proxy;
mod ipfs_stub;
mod proxy;

use clap::{Arg, App};
use cyfs_debug::{CyfsLoggerBuilder, PanicBuilder};
use cyfs_util::process::{ProcessAction, ProcessCmdFuncs, set_process_cmd_funcs};
use crate::ipfs_stub::IPFSStub;
use log::*;

const SERVICE_NAME: &str = "ipfs-proxy";

struct ExitFunc;
impl ProcessCmdFuncs for ExitFunc {
    fn exit_process(&self, action: ProcessAction, code: i32) -> ! {
        if action == ProcessAction::Stop {
            let _ = async_std::task::block_on(async {
                let stub = IPFSStub::new(None, None, None);
                stub.stop_ipfs().await;
            });
        }
        info!("exit process, action:{:?}, code:{}", action, code);
        std::process::exit(code);
    }
}

fn service_mutex_name() -> String {
    match std::env::current_exe() {
        Ok(path) => {
            let hash = cyfs_base::hash_data(path.display().to_string().as_bytes()).to_string();
            format!("{}-{}", SERVICE_NAME, &hash[..12])
        }
        Err(e) => {
            println!("call current_exe failed: {}", e);
            SERVICE_NAME.to_owned()
        }
    }
}

async fn main_run() {
    let app = App::new("ipfs proxy")
        .version(cyfs_base::get_version())
        .about("ipfs proxy, support accelerate ipfs by CYFS protocol")
        .arg(
            Arg::with_name("proxy-port")
                .long("proxy-port")
                .takes_value(true)
                .default_value("38091")
                .help("Specify ipfs-proxy proxy service's local port"),
        );

    let app = cyfs_util::process::prepare_args(app);
    let matches = app.get_matches();

    // 切换root目录
    match dirs::data_dir() {
        Some(dir) => {
            let dir = dir.join("cyfs");
            info!("will use user data dir: {}", dir.display());
            cyfs_util::bind_cyfs_root_path(dir);
        }
        None => {
            error!("get user data dir failed!");
        }
    };

    let root = cyfs_util::get_cyfs_root_path();
    if !root.is_dir() {
        if let Err(e) = std::fs::create_dir_all(&root) {
            error!("create root dir failed! dir={}, err={}", root.display(), e);
            std::process::exit(-1);
        }
    }

    let _ = set_process_cmd_funcs(Box::new(ExitFunc {}));

    #[cfg(target_os = "windows")]
    {
        // mutex在不同用户有独立的命名空间
        cyfs_util::process::check_cmd_and_exec_with_args(SERVICE_NAME, &matches);
    }
    #[cfg(not(target_os = "windows"))]
    {
        let service_mutex_name = service_mutex_name();
        println!("service mutex name: {}", service_mutex_name);

        cyfs_util::process::check_cmd_and_exec_with_args_ext(
            SERVICE_NAME,
            &service_mutex_name,
            &matches,
        );
    }

    CyfsLoggerBuilder::new_service(SERVICE_NAME)
        .level("info")
        .console("info")
        .build()
        .unwrap()
        .start();

    PanicBuilder::new("vfoggie", SERVICE_NAME).exit_on_panic(true).build().start();

    cyfs_debug::ProcessDeadHelper::instance().enable_exit_on_task_system_dead(None);

    let proxy_port = matches.value_of("proxy-port");
    let proxy_port = match proxy_port {
        Some(v) => v
            .parse()
            .map_err(|e| {
                println!("invalid proxy-port value: {}", e);
                std::process::exit(-1);
            })
            .unwrap(),
        None => 38090,
    };

    async_std::task::spawn(async move {
        let proxy = proxy::Proxy::new(proxy_port);
        if let Err(e) = proxy.start().await {
            error!("ipfs-proxy init failed: {}", e);
            std::process::exit(e.code().as_u16() as i32);
        }
    });

    async_std::future::pending::<u8>().await;
}

fn main() {
    cyfs_debug::ProcessDeadHelper::patch_task_min_thread();

    async_std::task::block_on(main_run())
}
