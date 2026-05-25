#pragma once
#include <vector>
#include <string>
#include <map>

using namespace std;

typedef struct STpixelStruct
{
	int r;
	int g;
	int b;
};
typedef struct STImageData
{
	int rows;
	int cols;
	vector<STpixelStruct>pixels;
};

class DicomData {
public:
	DicomData()
	{
		isLittleEdian = false;
		isExplicitVR = false;
		fileHeaderLen = 0;
		fileHeaderOffset = 0;
		pixDataOffset = 0;
		pxDataLen = 0;
		tags.clear();
		filename = "";
		windowCenter = 1000;
		windowWidth = 200;
		fileData = NULL;
	}
	int parseFile(string path);
	STImageData getImageData()
	{
		return imageData;
	}
	~DicomData()
	{
		if (fileData != NULL)
		{
			delete fileData;
			fileData = NULL;
		}
		
	}
	STImageData getImageData(int windowCenter, int windowWidth);
private:
	STImageData imageData;
	string filename;
	map<string, string> tags;
	unsigned int fileHeaderLen;
	long fileHeaderOffset;
	unsigned int pxDataLen;
	long pixDataOffset;//像素数据开始位置
	bool isLittleEdian;
	bool isExplicitVR;
	int windowCenter;
	int windowWidth;
	unsigned char* fileData;
	long fileLenth;
	string getVR(string tag);
	string getVF(string VR, vector<unsigned char>VF);
	int readTags(unsigned char* fileData, long fileLenth);
	bool getImage(unsigned char* filedata, long fileLength);
};