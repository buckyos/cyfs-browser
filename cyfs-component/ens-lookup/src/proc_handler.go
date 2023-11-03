package main

import (
    "fmt"
    "github.com/sirupsen/logrus"
    "io/ioutil"
    "net/http"
    "os"
    "os/exec"
    "path"
    "runtime"
    "strconv"
)

func getProfilePath() (string, error) {
    dataDir, err := os.UserConfigDir()
    if err != nil {
        return "", err
    }
    profilePath := path.Join(dataDir, "cyfs/run/enslookup.port")

    return profilePath, nil
}

func SaveProfile(port int) {
    profilePath, err := getProfilePath()
    if err != nil {
        logrus.Warnf("get profile path failed, err:%s", err)
        return
    }
    file, err := os.OpenFile(profilePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
    if err != nil {
        logrus.Warnf("open profile failed. file:%s err:%s", profilePath, err)
        return
    }

    defer file.Close()

    _, err = fmt.Fprint(file, port)
    if err != nil {
        // 处理错误
        logrus.Warnf("write profile failed. file:%s err:%s", profilePath, err)
    }
}

func StopProc() {
    profilePath, err := getProfilePath()
    if err != nil {
        logrus.Warnf("get profile path failed, err:%s", err)
        return
    }

    data, err := ioutil.ReadFile(profilePath)
    if err != nil {
        logrus.Warnf("read profile failed. err:%s", err)
        return
    }

    port, err := strconv.Atoi(string(data))
    if err != nil {
        logrus.Warnf("parse profile failed, err:%s", err)
        return
    }

    url := fmt.Sprintf("http://127.0.0.1:%d/forceexit", port)

    http.Get(url)

    //Kill for sure
    if runtime.GOOS == "windows" {
        cmd := exec.Command("taskkill", "/F", "/IM", "enslookup.exe")
        cmd.Run()
    } else {
        cmd := exec.Command("killall", "enslookup")
        cmd.Run()
    }
}
