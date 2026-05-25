#pragma once

#include <QtWidgets/QWidget>
#include "ui_DicomViewer.h"
#include "DicomHelper.h"
class DicomViewer : public QWidget
{
    Q_OBJECT

public:
    DicomViewer(QWidget *parent = Q_NULLPTR);

private:
    Ui::DicomViewerClass ui;
    DicomData m_data;
    int windowCenter;
    int windowWidth;
    QImage m_image;
    unsigned char* imageBinaryData;
    void makeImg();
public slots:
    void onResetClicked();
    void openDicomFile();
};
