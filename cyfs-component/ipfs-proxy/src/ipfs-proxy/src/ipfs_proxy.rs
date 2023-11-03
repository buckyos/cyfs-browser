use std::path::Path;
use std::str::FromStr;
use std::sync::{Arc, RwLock};
use async_trait::async_trait;
use log::*;
use cyfs_base::{BuckyError, BuckyErrorCode};
use http_types::{StatusCode};
use tide::{Redirect};
use crate::ipfs_stub::IPFSStub;

#[derive(PartialEq)]
enum IpfsDaemonStatus {
    Disable,
    Running,
    NotInit,
    NotRunning,
    Starting
}

#[derive(Clone)]
pub struct IpfsProxy(Arc<IpfsProxyInner>);

pub struct IpfsProxyInner {
    ipfs_gateway_port: u16,
    stub: IPFSStub,

    status: RwLock<IpfsDaemonStatus>
}

impl IpfsProxy {
    pub(crate) fn new(ipfs_gateway_port: u16) -> Self {
        info!("create ipfs proxy, local gateway port {}", ipfs_gateway_port);
        let stub = IPFSStub::new(None, None, None);
        let status = if stub.is_valid() {
            IpfsDaemonStatus::NotInit
        } else {
            warn!("ipfs daemon not found at {}, disable ipfs proxy", stub.ipfs_prog_path().display());
            IpfsDaemonStatus::Disable
        };

        Self(Arc::new(IpfsProxyInner {
            ipfs_gateway_port,
            stub,
            status: RwLock::new(status)
        }))
    }

    pub(crate) fn start_ipfs(&self) {
        if *self.0.status.read().unwrap() == IpfsDaemonStatus::Disable {
            return;
        }
        let inner = self.0.clone();
        async_std::task::spawn(async move {
            *inner.status.write().unwrap() = IpfsDaemonStatus::Starting;
            if !inner.stub.is_init().await {
                if let Err(e) = inner.stub.init().await {
                    error!("ipfs init err {}", e);
                    *inner.status.write().unwrap() = IpfsDaemonStatus::NotRunning;
                }
            }

            if let Err(e) = inner.stub.set_port(inner.ipfs_gateway_port, inner.ipfs_gateway_port+1, inner.ipfs_gateway_port+2).await {
                error!("ipfs set port err {}", e);
                *inner.status.write().unwrap() = IpfsDaemonStatus::NotRunning;
            }

            if inner.stub.start().await {
                *inner.status.write().unwrap() = IpfsDaemonStatus::Running;
            } else {
                *inner.status.write().unwrap() = IpfsDaemonStatus::NotRunning;
            }
        });
    }

    fn is_ipns(path: &Path) -> bool {
        return path.starts_with("/ipns")
    }
}

// List of acceptible 300-series redirect codes.
const REDIRECT_CODES: &[StatusCode] = &[
    StatusCode::MovedPermanently,
    StatusCode::Found,
    StatusCode::SeeOther,
    StatusCode::TemporaryRedirect,
    StatusCode::PermanentRedirect,
];

impl IpfsProxyInner
{
    fn check_status(&self) -> Result<(), tide::Error> {
        match *self.status.read().unwrap() {
            IpfsDaemonStatus::Running => Ok(()),
            IpfsDaemonStatus::Disable => Err(tide::Error::new(tide::StatusCode::ServiceUnavailable, BuckyError::new(BuckyErrorCode::UnSupport, "ipfs proxy disable"))),
            IpfsDaemonStatus::NotInit => Err(tide::Error::new(tide::StatusCode::ServiceUnavailable, BuckyError::new(BuckyErrorCode::NotInit, "ipfs proxy not inited"))),
            IpfsDaemonStatus::NotRunning => Err(tide::Error::new(tide::StatusCode::ServiceUnavailable, BuckyError::new(BuckyErrorCode::UnSupport, "ipfs proxy daemon start error"))),
            IpfsDaemonStatus::Starting => Err(tide::Error::new(tide::StatusCode::ServiceUnavailable, BuckyError::new(BuckyErrorCode::UnSupport, "ipfs proxy daemon starting, please wait"))),
        }
    }

    async fn call<State>(&self, req: tide::Request<State>) -> tide::Result
    where
        State: Clone + Send + Sync + 'static,
    {
        self.check_status()?;
        let url = req.url();
        let path = Path::new(url.path());
        if IpfsProxy::is_ipns(path) {
            info!("ipfs proxy recv ipns req path {}", path.display());
            let mut new_req: http_types::Request = req.into();
            new_req.url_mut().set_port(Some(self.ipfs_gateway_port)).unwrap();
            self.respond(new_req).await
        } else {
            info!("ipfs proxy recv req path {}, treat as ipfs path", path.display());
            let mut new_req: http_types::Request = req.into();
            new_req.url_mut().set_port(Some(self.ipfs_gateway_port)).unwrap();
            self.respond(new_req).await
        }
    }

    async fn respond(&self, mut req: http_types::Request) -> tide::Result {
        let mut old_path_parts = req.url().path().split("/").collect::<Vec<&str>>();
        if old_path_parts.len() > 2 && old_path_parts[1] == "ipfs" {
            if let Ok(cid) = cid::Cid::from_str(old_path_parts[2]) {
                if cid.version() == cid::Version::V0 {
                    if let Ok(cid) = cid.into_v1() {
                        let new_cid = cid.to_string();
                        old_path_parts[2] = &new_cid;
                        let new_path = old_path_parts.join("/");
                        info!("convert path {} to {}", req.url().path(), &new_path);
                        return Ok(Redirect::permanent(new_path).into())
                    }
                }
            }
        }
        let address = format!("{}:{}", req.url().host_str().unwrap(), req.url().port().unwrap());
        let stream = async_std::net::TcpStream::connect(&address).await.map_err(|e|{
            error!("connect to {} err {}", &address, e);
            tide::Error::new(StatusCode::InternalServerError, e)
        })?;
        info!("redirect req to {}", req.url());
        let resp = async_h1::connect(stream, req.clone()).await.map(tide::Response::from_res)?;
        info!("got response from {}, code {}", req.url(), resp.status());
        Ok(resp)
    }
}

#[async_trait]
impl<State> tide::Endpoint<State> for IpfsProxy
    where
        State: Clone + Send + Sync + 'static,
{
    async fn call(&self, req: tide::Request<State>) -> tide::Result {
        self.0.call(req).await
    }
}