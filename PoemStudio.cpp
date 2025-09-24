/* write by DogMonkeys */
/* 主程序入口,执行解释器命令 */

//please build by qtcreator

#include <QApplication>
#include <QProcess>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QProcess p;
    p.start("pyPlugin\\python_.exe PoemStudio.pyc");
    p.waitForStarted();
    p.waitForFinished();
    return a.exec();
}
