#include "DicomViewer.h"
#include <QtWidgets/QApplication>
#include "DicomHelper.h"
int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    DicomViewer w;
    w.show();
    return a.exec();
}
