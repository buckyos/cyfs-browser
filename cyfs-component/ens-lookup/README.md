# ens-lookup

Components that provide [ens](https://ens.domains/about/) lookup functionality

1. will listen to http requests locally (default: 127.0.0.1:38098) and return the query results, see [config.toml](https://github.com/glen0125/ens-lookup/blob/main/config.toml) for configuration, or pass in port via the Command line parameters passed into the port.

2. The request is usually: http://127.0.0.1:38090/forward/{ensDomain}

3. Supports setting the provider via configuration file or dynamically configuring the service in code.

4. At least one query provider is needed, you can go to [infura](https://docs.infura.io/networks/ethereum/how-to/secure-a-project/project-id) to apply for it, but generally there are limits on the number and frequency of queries.