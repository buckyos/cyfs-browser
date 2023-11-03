use cyfs_base::BuckyResult;
use tide::http::headers::HeaderValue;
use tide::security::{CorsMiddleware, Origin};

use log::*;
use tide::prelude::*;
use crate::ipfs_proxy::IpfsProxy;

pub(crate) struct Proxy {
    server: tide::Server<()>,
    proxy_port: u16
}

impl Proxy {
    pub fn new(proxy_port: u16) -> Self {
        let mut server = ::tide::new();
        let cors = CorsMiddleware::new()
            .allow_methods(
                "GET, POST, PUT, DELETE, OPTIONS"
                    .parse::<HeaderValue>()
                    .unwrap(),
            )
            .allow_origin(Origin::from("*"))
            .allow_credentials(true)
            .allow_headers("*".parse::<HeaderValue>().unwrap())
            .expose_headers("*".parse::<HeaderValue>().unwrap());
        server.with(cors);

        let ipfs_proxy = IpfsProxy::new(proxy_port+1);
        ipfs_proxy.start_ipfs();
        server.at("/ipfs/*").get(ipfs_proxy.clone());
        server.at("/ipns/*").get(ipfs_proxy);

        Self {
            server,
            proxy_port
        }
    }

    pub async fn start(self) -> BuckyResult<()> {
        let addr = format!("127.0.0.1:{}", self.proxy_port);
        let mut listener = self.server.bind(&addr).await.map_err(|e| {
            error!("ipfs-proxy port bind error! addr={}, {}", addr, e);
            e
        })?;

        for info in listener.info().iter() {
            info!(
                "ipfs-proxy http server listening on addr={}, info={}",
                addr, info
            );
        }

        if let Err(e) = listener.accept().await {
            error!("http server accept error! addr={}, {}", addr, e);
        }

        Ok(())
    }
}