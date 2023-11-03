package main

import (
    "enslookup/ensresolver"
    "enslookup/log"
    "flag"
    "fmt"
    "os"
    "path"
    "runtime"
    "strings"

    "github.com/BurntSushi/toml"
    "github.com/kataras/iris/v12"
    //"github.com/kataras/iris/v12/middleware/logger"
    "github.com/sirupsen/logrus"
)

var DEFAULT_PORT = 38099

var (
    // Version is the version of this program.
    Version string
)

type Config struct {
    LogLevel string `toml:"log_level"`
    //ListenPort int    `toml:"listen_port"`
    Eth struct {
        Providers []string `toml:"providers"`
    }
}

func loadConfig() *Config {
    dataDir, err := os.UserConfigDir()
    if err != nil {
        logrus.Warnf("get appdata dir failed, err:%s", err)
        return nil
    }
    configPath := path.Join(dataDir, "cyfs/etc/runtime/enslookup.toml")
    var conf Config
    logrus.Info("will load config from:", configPath)
    _, err = toml.DecodeFile(configPath, &conf)
    if err != nil {
        logrus.Info("load config failed. err:", err, "will use default config")
        return nil
    }
    logrus.Info("load config:", conf)

    return &conf
}

func main() {
    log.InitiLogger()
    logrus.Info("Version:", Version, " OS:", runtime.GOOS)

    var isStop bool
    var listenPort int
    flag.IntVar(&listenPort, "port", 38099, "port")
    flag.BoolVar(&isStop, "stop", false, "stop")

    flag.Parse()

    if isStop {
        logrus.Info("will stop enslookup")
        StopProc()
        return
    } else {
        SaveProfile(listenPort)
    }

    conf := loadConfig()
    if conf != nil && conf.LogLevel != "" {
        log.SetLogLevel(conf.LogLevel)
    }
    ethProviders := []string{}
    if conf != nil {
        ethProviders = conf.Eth.Providers
    }
    resolver, err := ensresolver.InitEnsResolver(ethProviders)
    if err != nil {
        panic(err)
    }

    HandleEnsUri := func(ctx iris.Context) {
        userAgent := ctx.Request().UserAgent()
        if !(strings.Contains(userAgent, "CYFS Browser") || strings.Contains(userAgent, "Kalama")) {
            ctx.Writef("Invalid Request")
            return
        }
        fullPath := ctx.Request().RequestURI
        ensDomain := ctx.Params().GetStringTrim("ensDomain")
        logrus.Debug("url path:", fullPath, ", will resolve domain:", ensDomain)

        res, err := resolver.Resolve(ensDomain)
        if res != "" && err == nil {
            lastPartIndex := strings.Index(fullPath, ensDomain)
            lastPart := fullPath[lastPartIndex+len(ensDomain):]
            redirectUrl := res + lastPart
            logrus.Infof("will redirect url [%s] to [%s]", fullPath, redirectUrl)
            ctx.Redirect(redirectUrl)
            return
        }

        originalPartIndex := strings.Index(fullPath, "/forward/")
        redirectUrl := "http://" + fullPath[originalPartIndex+len("/forward/"):]
        logrus.Warnf("cannot resolve %s, pass it. err:%s", ensDomain, err)
        logrus.Infof("will redirect url [%s] to [%s]", fullPath, redirectUrl)
        ctx.Redirect(redirectUrl)
    }

    app := iris.New()
    //app.Use(logger.New())

    app.Get("/forward/{ensDomain:string}/{others:path}", HandleEnsUri)

    app.Get("/forward/{ensDomain:string}", HandleEnsUri)

    app.Get("/forceexit", func(_ iris.Context) {
        logrus.Info("recv force exit, will exit")
        os.Exit(0)
    })

    listenAddr := fmt.Sprintf("127.0.0.1:%d", listenPort)
    //logrus.Info("will listen at: ", listenAddr)
    app.Listen(listenAddr)
}
