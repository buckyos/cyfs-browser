package log

import (
    "fmt"
    //rotatelogs "github.com/lestrrat-go/file-rotatelogs"
    "bytes"
    //nested "github.com/antonfisher/nested-logrus-formatter"
    "github.com/sirupsen/logrus"
    "gopkg.in/natefinch/lumberjack.v2"
    "io"
    "os"
    "path"
    //"runtime"
)

type MyFormatter struct{}

var DEFAULT_LEVEL = logrus.InfoLevel

func (m *MyFormatter) Format(entry *logrus.Entry) ([]byte, error) {
    var b *bytes.Buffer
    if entry.Buffer != nil {
        b = entry.Buffer
    } else {
        b = &bytes.Buffer{}
    }

    timestamp := entry.Time.Format("2006-01-02 15:04:05.000")
    var newLog string

    //HasCaller()为true才会有调用信息
    if entry.HasCaller() {
        fName := path.Base(entry.Caller.File)
        newLog = fmt.Sprintf("[%s] [%s] [%s:%d] %s\n",
            timestamp, entry.Level, fName, entry.Caller.Line, entry.Message)
    } else {
        newLog = fmt.Sprintf("[%s] [%s] %s\n", timestamp, entry.Level, entry.Message)
    }

    b.WriteString(newLog)
    return b.Bytes(), nil
}

func SetLogLevel(logLevel string) {
    lv, err := logrus.ParseLevel(logLevel)
    if err == nil {
        logrus.SetLevel(lv)
    } else {
        logrus.SetLevel(DEFAULT_LEVEL)
    }
}

func InitiLogger() {
    logrus.SetReportCaller(true)
    logrus.SetFormatter(&MyFormatter{})
    dataDir, err := os.UserConfigDir()
    if err != nil {
        logrus.Fatalf("get appdata failed, err:%s", err)
    }
    logPath := fmt.Sprintf("%s/cyfs/log/enslookup", dataDir)
    if err := os.MkdirAll(logPath, os.ModePerm); err != nil {
        logrus.Fatal("create log dir failed, err:", err)
    }
    logrus.Debug("will store log in", logPath)

    // fileWriter, err := rotatelogs.New(
    //     fmt.Sprintf("%s/enslookup_%d_%s.log", logPath, os.Getpid(), time.Now().Format("2006-01-02_15.04.05")),
    //     //rotatelogs.WithLinkName(fmt.Sprintf("%s/enslookup_%d_current.log", logPath, os.Getpid())),
    //     rotatelogs.WithMaxAge(-1),
    //     rotatelogs.WithRotationCount(5),
    //     //rotatelogs.WithRotationTime(time.Second*10),
    //     rotatelogs.WithRotationSize(1*500),
    // )
    // if err != nil {
    //     logrus.Fatalf("Failed to initialize log file %s", err)
    // }

    fileLogger := &lumberjack.Logger{
        Filename:   fmt.Sprintf("%s/enslookup_%d.log", logPath, os.Getpid()),
        MaxSize:    3, // megabytes
        MaxBackups: 3,
        MaxAge:     30, //days
        LocalTime:  true,
        Compress:   false, // disabled by default
    }

    logrus.SetOutput(io.MultiWriter(os.Stdout, fileLogger))
}
