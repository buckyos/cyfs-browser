package ensresolver

import (
    "crypto/aes"
    "crypto/cipher"
    "encoding/hex"
    "encoding/json"
    "errors"
    "fmt"
    "github.com/ethereum/go-ethereum/ethclient"
    "github.com/sirupsen/logrus"
    ens "github.com/wealdtech/go-ens/v3"
    "io/ioutil"
    "net/http"
    "strings"
    "sync"
)

var DEFAULT_PROVIDERS = []string{
    "https://mainnet.infura.io/v3/xxxxxxxx",
}

/*Provider's configuration service. 
The returned data will be merged with the default provider. 
The returned provider will be used with priority.
*/
var PROVIDER_CONFIG_URL = "https://query.com/ethprovider"

type EnsCache struct {
    cache map[string]string
    lock  sync.RWMutex
}

func NewEnsCache() *EnsCache {
    return &EnsCache{
        cache: make(map[string]string),
    }
}

func (ec *EnsCache) Set(domain, value string) {
    logrus.Infof("save domain [%s]: [%s] in cache", domain, value)
    ec.lock.Lock()
    defer ec.lock.Unlock()
    ec.cache[domain] = value
}

func (ec *EnsCache) Get(domain string) (string, bool) {
    ec.lock.RLock()
    defer ec.lock.RUnlock()
    r, ok := ec.cache[domain]
    return r, ok
}

type EnsResolver struct {
    providers []string
    ensCache  *EnsCache
}

func mergeProviders(prv1 []string, prv2 []string) []string {
    var mergedMap = make(map[string]int, len(prv1)+len(prv2))
    var result = []string{}

    for _, v := range prv1 {
        _, ok := mergedMap[v]
        if ok {
            continue
        }
        mergedMap[v] = 0
        result = append(result, v)
    }
    for _, v := range prv2 {
        _, ok := mergedMap[v]
        if ok {
            continue
        }
        mergedMap[v] = 0
        result = append(result, v)
    }

    return result
}

func InitEnsResolver(providersInConfig []string) (*EnsResolver, error) {
    remoteProviders := getProviderFromServer()
    logrus.Infof("fetch %d providers", len(remoteProviders))
    innerProvider := mergeProviders(remoteProviders, DEFAULT_PROVIDERS)
    providers := mergeProviders(providersInConfig, innerProvider)
    //logrus.Info("after merge, providers:", providers)

    return &EnsResolver{
        providers: providers,
        ensCache:  NewEnsCache(),
    }, nil
}

func FixContentHash(hash string) string {
    hashLen := len(hash)
    if hashLen >= 6 {
        firstPart := hash[0:6]
        fixed := ""
        if firstPart == "/ipfs/" {
            fixed = "ipfs://" + hash[6:]
        } else if firstPart == "/ipns/" {
            fixed = "ipns://" + hash[6:]
        }

        if fixed != "" {
            logrus.Infof("fix content hash from [%s] to [%s]", hash, fixed)
            return fixed
        }
    }
    return hash
}

//link is not ipfs or ipns, use ${domain}.link
func IsNeedLinkSuffix(hash string) bool {
    schemeEndIndex := strings.Index(hash, "://")
    if schemeEndIndex > 0 {
        scheme := hash[0:schemeEndIndex]
        if scheme == "bzz" || scheme == "onion" || scheme == "onion3" || scheme == "sia" {
            return true
        }
    }
    return false
}

func (p *EnsResolver) Resolve(ensDomain string) (string, error) {
    res, ok := p.ensCache.Get(ensDomain)
    if ok {
        if res == "" {
            logrus.Infof("find domain [%s] in cache, but is unregistered name", ensDomain)
            return "", errors.New("unregistered name")
        }
        logrus.Infof("find domain [%s]: [%s] in cache", ensDomain, res)
        return res, nil
    }
    providerIndex := 0
    for _, provider := range p.providers {
        providerIndex++
        logrus.Debugf("will resolve ens domain [%s] with provider [%d]", ensDomain, providerIndex)
        client, err := ethclient.Dial(provider)
        if err != nil {
            logrus.Warnf("create eth client with provider [%s] failed. err:%s", providerIndex, err)
            continue
        }

        resolver, err := ens.NewResolver(client, ensDomain)
        if err != nil {
            logrus.Warnf("create resolver failed. domain [%s], provider [%d], err:%s", ensDomain, providerIndex, err)
            if err.Error() == "unregistered name" {
                //domain is unregistered, no need query other providers
                logrus.Infof("domain [%s] is unregistered. store and pass it", ensDomain)
                p.ensCache.Set(ensDomain, "")
                return "", err
            }
            continue
        }

        contentHash, err := resolver.Contenthash()
        if err != nil {
            logrus.Warnf("get content hash failed. domain [%s], provider [%s], err:%s", ensDomain, providerIndex, err)
            continue
        }

        result, err := ens.ContenthashToString(contentHash)
        if err != nil {
            logrus.Warnf("convert content hash to string failed. domain [%s], err:%s", ensDomain, err)
            continue
        }

        if IsNeedLinkSuffix(result) {
            logrus.Infof("domain is not ipfs/ipns, add link suffix. domain [%s], result [%s]", ensDomain, result)
            result = "http://" + ensDomain + ".link"
        } else {
            result = FixContentHash(result)
        }

        //remove last "/"
        if result[len(result)-1:] == "/" {
            result = result[0 : len(result)-1]
        }

        logrus.Infof("resolve [%s] to [%s] via provide: [%d]", ensDomain, result, providerIndex)

        p.ensCache.Set(ensDomain, result)

        return result, err
    }

    logrus.Errorf("resolve domain [%s] failed.", ensDomain)

    return "", fmt.Errorf("cannot resolve domain [%s]", ensDomain)
}

/*
If you have your own provider query service, 
you need to modify this to your own query logic here.
*/
func getProviderFromServer() []string {
    var providers []string = make([]string, 0)
    resp, err := http.Get(PROVIDER_CONFIG_URL)
    if err != nil {
        return providers
    }

    defer resp.Body.Close()

    data, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        logrus.Warn("get provider failed. err:", err, data)
        return providers
    }

    err = json.Unmarshal([]byte(data), &providers)
    if err != nil {
        logrus.Warn("parse provider failed. err:", err)
    }

    return providers
}
