
#ifndef COMPONENTS_API_REQUEST_HELPER_API_REQUEST_HELPER_H_
#define COMPONENTS_API_REQUEST_HELPER_API_REQUEST_HELPER_H_

#include <list>
#include <memory>
#include <string>

#include "base/callback.h"
#include "base/containers/flat_map.h"
#include "net/traffic_annotation/network_traffic_annotation.h"
#include "url/gurl.h"

namespace network {
class SharedURLLoaderFactory;
class SimpleURLLoader;
}  // namespace network

namespace api_request_helper {

// Anyone is welcome to use APIRequestHelper to reduce boilerplate
class APIRequestHelper {
 public:
  APIRequestHelper(
      net::NetworkTrafficAnnotationTag annotation_tag,
      scoped_refptr<network::SharedURLLoaderFactory> url_loader_factory);
  ~APIRequestHelper();

  using ResultCallback =
      base::OnceCallback<void(const int,
                              const std::string&,
                              const base::flat_map<std::string, std::string>&)>;
  void Request(const std::string& method,
               const GURL& url,
               const std::string& payload,
               const std::string& payload_content_type,
               bool auto_retry_on_network_change,
               ResultCallback callback,
               const base::flat_map<std::string, std::string>& headers = {},
               size_t max_body_size = -1u);

 private:
  APIRequestHelper(const APIRequestHelper&) = delete;
  APIRequestHelper& operator=(const APIRequestHelper&) = delete;
  using SimpleURLLoaderList =
      std::list<std::unique_ptr<network::SimpleURLLoader>>;
  void OnResponse(SimpleURLLoaderList::iterator iter,
                  ResultCallback callback,
                  const std::unique_ptr<std::string> response_body);

  net::NetworkTrafficAnnotationTag annotation_tag_;
  SimpleURLLoaderList url_loaders_;
  scoped_refptr<network::SharedURLLoaderFactory> url_loader_factory_;
};

}  // namespace api_request_helper

#endif  // COMPONENTS_API_REQUEST_HELPER_API_REQUEST_HELPER_H_
