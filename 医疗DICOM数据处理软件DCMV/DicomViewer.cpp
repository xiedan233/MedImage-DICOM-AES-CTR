#include "DicomViewer.h"
#include "DicomHelper.h"
#include <QImage>
#include <QFileDialog>
static unsigned int color2Int(int r,int g,int b)
{
	int a = 255;
	unsigned int color = (a<< 24 & 0xFF000000) |
		(r << 16 & 0x00FF0000) |
		(g << 168 & 0x0000FF00) |
		(b & 0x000000FF);
	return color;
}
DicomViewer::DicomViewer(QWidget *parent)
    : QWidget(parent)
{
    ui.setupUi(this);
	imageBinaryData = NULL;
	connect(ui.pushButton_adjust, SIGNAL(clicked()), this, SLOT(onResetClicked()));;
	connect(ui.pushButton_file, SIGNAL(clicked()), this, SLOT(openDicomFile()));
	windowCenter = 1000;
	windowWidth = 200;
	//m_data.parseFile("IM0");
	//STImageData imgdata = m_data.getImageData();
	ui.lineEdit_pos->setText(QString::number(windowCenter));
	ui.lineEdit_width->setText(QString::number(windowWidth));
	//makeImg();
	//ui.label_image->setPixmap(QPixmap::fromImage(m_image));
	QImage image = QImage(512, 512,QImage::Format_Grayscale8);
	ui.label_image->setPixmap(QPixmap::fromImage(image));
}
void DicomViewer::onResetClicked()
{
	QString ww = ui.lineEdit_width->text();
	QString wp = ui.lineEdit_pos->text();
	windowCenter = wp.toInt();
	windowWidth = ww.toInt();
	makeImg();
	ui.label_image->setPixmap(QPixmap::fromImage(m_image));

}
void DicomViewer::makeImg()
{
	STImageData imgdata = m_data.getImageData(windowCenter, windowWidth);
	m_image = QImage(imgdata.rows, imgdata.cols, QImage::Format_Grayscale8);
	int bytePerLine = m_image.bytesPerLine();
	int dataSize = imgdata.rows * imgdata.cols;
	if (imageBinaryData != NULL)
	{
		delete[] imageBinaryData;
		imageBinaryData = NULL;
	}
	imageBinaryData = new unsigned char[dataSize];
	for (int i = 0; i < imgdata.rows; i++)
	{
		for (int j = 0; j < imgdata.cols; j++)
		{
			int curPos = i * imgdata.rows + j;
			imageBinaryData[curPos] = imgdata.pixels[curPos].r;
		}
	}
	m_image = QImage(imageBinaryData, imgdata.rows, imgdata.cols, QImage::Format_Grayscale8);
	m_image = m_image.scaled(512, 512, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
}

void DicomViewer::openDicomFile()
{
	QFileDialog* dlg = new QFileDialog(this);
	dlg->setWindowTitle(QString::fromLocal8Bit("打开文件"));
	dlg->setFileMode(QFileDialog::ExistingFile);
	QString fileName;
	if (dlg->exec())
	{
		QStringList files = dlg->selectedFiles();
		if (files.size() == 0)
		{
			return;
		}
		fileName = files.at(0);
	}
	if (fileName.length() <= 0)
	{
		return;
	}
	ui.lineEdit_file->setText(fileName);
	m_data.parseFile(fileName.toLocal8Bit().data());
	makeImg();
	ui.label_image->setPixmap(QPixmap::fromImage(m_image));
}
