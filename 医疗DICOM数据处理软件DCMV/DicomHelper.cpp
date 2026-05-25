#include "DicomHelper.h"
#include <stdio.h>
#define ST_INT_MAX (2147483647)
#define ST_UINT_MAX (0XFFFFFFFF)
typedef union ST_NUM {
	double v_d;
	float v_f;
	int v_i;
	unsigned int v_ui;
	unsigned short v_us;
	short v_s;
	unsigned char a[8];
};
enum ST_NUM_TYPE {
	ST_TYPE_UINT16 = 1,
	ST_TYPE_INT16,
	ST_TYPE_UINT32,
	ST_TYPE_INT32,
	ST_TYPE_FLOAT,
	ST_TYPE_DOUBLE
};

string getNumString(ST_NUM_TYPE type, vector<unsigned char>VF)
{
	char numstr[100];
	memset(numstr, 0, sizeof(numstr));
	ST_NUM num;

	if (type == ST_TYPE_UINT16)
	{
		num.a[0] = VF[0];
		num.a[1] = VF[1];
		itoa(num.v_us, numstr, 10);
	}
	else if (type == ST_TYPE_INT16)
	{
		num.a[0] = VF[0];
		num.a[1] = VF[1];
		itoa(num.v_s, numstr, 10);
	}
	else if (type == ST_TYPE_UINT32)
	{
		num.a[0] = VF[0];
		num.a[1] = VF[1];
		num.a[2] = VF[2];
		num.a[3] = VF[3];
		itoa(num.v_ui, numstr, 10);
	}
	else if (type == ST_TYPE_INT32)
	{
		num.a[0] = VF[0];
		num.a[1] = VF[1];
		num.a[2] = VF[2];
		num.a[3] = VF[3];
		itoa(num.v_i, numstr, 10);
	}
	else if (type == ST_TYPE_FLOAT)
	{
		num.a[0] = VF[0];
		num.a[1] = VF[1];
		num.a[2] = VF[2];
		num.a[3] = VF[3];
		sprintf(numstr, "%f", num.v_f);
	}
	else if (type == ST_TYPE_DOUBLE)
	{
		num.a[0] = VF[0];
		num.a[1] = VF[1];
		num.a[2] = VF[2];
		num.a[3] = VF[3];
		num.a[4] = VF[4];
		num.a[5] = VF[5];
		num.a[6] = VF[6];
		num.a[7] = VF[7];
		sprintf(numstr, "%f", num.v_d);
	}
	return numstr;
}

string DicomData::getVR(string tag)
{
	if(tag =="0002,0000")//文件元信息长度
		return "UL";
	if(tag =="0002,0010")//传输语法
		return "UI";
	if (tag == "0002,0013")//文件生成程序的标题
		return "SH";
	if(tag == "0008,0005")//文本编码
		return "CS";
	if (tag == "0008,0008")
		return "CS";
	if (tag == "0008,1032")//成像时间
		return "SQ";
	if (tag == "0008,1111")
		return "SQ";
	if (tag == "0008,0020")//检查日期
		return "DA";
	if (tag == "0008,0060")//成像仪器
		return "CS";
	if (tag == "0008,0070")//成像仪厂商
		return "LO";
	if (tag == "0008,0080")
		return "LO";
	if (tag == "0010,0010")//病人姓名
		return "PN";
	if (tag == "0010,0020")//病人id
		return "LO";
	if (tag == "0010,0030")//病人生日
		return "DA";
	if (tag == "0018,0060")//电压
		return "DS";
	if (tag == "0018,1030")//协议名
		return "LO";
	if (tag == "0018,1151")
		return "IS";
	if (tag == "0020,0010")//检查ID
		return "SH";
	if (tag == "0020,0011")//序列
		return "IS";
	if (tag == "0020,0012")//成像编号
		return "IS";
	if (tag == "0020,0013")//影像编号
		return "IS";
	if (tag == "0028,0002")//像素采样1为灰度3为彩色
		return "US";
	if (tag == "0028,0004")//图像模式MONOCHROME2为灰度
		return "CS";
	if (tag == "0028,0010")//row高
		return "US";
	if (tag == "0028,0011")//col宽
		return "US";
	if (tag == "0028,0100")//单个采样数据长度
		return "US";
	if (tag == "0028,0101")//实际长度
		return "US";
	if (tag == "0028,0102")//采样最大值
		return "US";
	if (tag == "0028,1050")//窗位
		return "DS";
	if (tag == "0028,1051")//窗宽
		return "DS";
	if (tag == "0028,1052")
		return "DS";
	if (tag == "0028,1053")
		return "DS";
	if (tag == "0040,0008")//文件夹标签
		return "SQ";
	if (tag == "0040,0260")//文件夹标签
		return "SQ";
	if (tag == "0040,0275")//文件夹标签
		return "SQ";
	if (tag == "7fe0,0010")//像素数据开始处
		return "OW";
	
	return "UN";
	
}

string DicomData::getVF(string VR, vector<unsigned char>VF)
{
	string vfStr = "";
	if (VF.size() == 0)
	{
		return vfStr;
	}
	if (VR == "SS")
	{		
		vfStr = getNumString(ST_TYPE_INT16,VF);
	}
	else if (VR == "US")
	{
		vfStr = getNumString(ST_TYPE_UINT16, VF);
	}
	else if (VR == "SL")
	{
		vfStr = getNumString(ST_TYPE_INT32, VF);
	}
	else if (VR == "UL")
	{
		vfStr = getNumString(ST_TYPE_UINT32, VF);
	}
	else if (VR == "AT")
	{
		vfStr = getNumString(ST_TYPE_UINT16, VF);
	}
	else if (VR == "FL")
	{
		vfStr = getNumString(ST_TYPE_FLOAT, VF);
	}
	else if (VR == "FD")
	{
		vfStr = getNumString(ST_TYPE_DOUBLE, VF);
	}
	else if (VR == "OB" || VR == "OW" || VR == "SQ" || VR == "OF" || VR == "UT")
	{
		vfStr = (char*)VF.data();
	}
	else {
		vfStr = (char*)VF.data();
	}

	return vfStr;
}

int DicomData::readTags(unsigned char* fileData, long fileLenth)
{
	bool enDir = false;
	int level = 0;
	string flodertag = "";
	vector<char>floderData;
	int startPos = 132;
	while (startPos + 6 < fileLenth)
	{
		char tag[10];
		sprintf(tag, "%02x", fileData[startPos + 1]);
		sprintf(tag + 2, "%02x", fileData[startPos]);
		tag[4] = ',';
		sprintf(tag + 5, "%02x", fileData[startPos + 3]);
		sprintf(tag + 7, "%02x", fileData[startPos + 2]);
		tag[9] = '\0';
		startPos += 4;
		string VR = "";
		string stag = tag;
		if (stag == "0028,0010")
		{
			printf("hh");
		}if (stag == "7fe0,0010")
		{
			printf("hh");
		}
		if (stag == "0008,0005")
		{
			printf("hh");
		}
		unsigned int len = 0;
		if (stag.substr(0, 4) == "0002")
		{
			VR += fileData[startPos];
			startPos++;
			VR += fileData[startPos];
			startPos++;
			if (VR == "OB" || VR == "OW" || VR == "SQ" || VR == "OF" || VR == "UT" || VR == "UN")
			{
				startPos += 2;
				ST_NUM num;
				num.a[0] = fileData[startPos];
				num.a[1] = fileData[startPos + 1];
				num.a[2] = fileData[startPos + 2];
				num.a[3] = fileData[startPos + 3];
				len = num.v_ui;
				startPos += 4;
			}
			else
			{
				
				ST_NUM num;
				num.a[0] = fileData[startPos];
				num.a[1] = fileData[startPos + 1];
				len = num.v_us;
				startPos += 2;
			}
		}
		else if (stag == "fffe,e000" || stag == "fffe,e00d" || stag == "fffe,e0dd")//文件夹标签
		{
			VR = "**";
			ST_NUM num;
			//startPos += 2;
			num.a[0] = fileData[startPos];
			num.a[1] = fileData[startPos + 1];
			num.a[2] = fileData[startPos + 2];
			num.a[3] = fileData[startPos + 3];
			len = num.v_ui;
			startPos += 4;
		}
		else if (isExplicitVR == true)//有无VR的情况
		{
			VR += fileData[startPos];
			startPos++;
			VR += fileData[startPos];
			startPos++;

			if (VR == "OB" || VR == "OW" || VR == "SQ" || VR == "OF" || VR == "UT" || VR == "UN")
			{
				ST_NUM num;
				startPos += 2;
				num.a[0] = fileData[startPos];
				num.a[1] = fileData[startPos + 1];
				num.a[2] = fileData[startPos + 2];
				num.a[3] = fileData[startPos + 3];
				len = num.v_ui;
				startPos += 4;
			}
			else
			{
				ST_NUM num;
				num.a[0] = fileData[startPos];
				num.a[1] = fileData[startPos + 1];
				len = num.v_us;
				startPos += 2;
			}
		}
		else if (isExplicitVR == false)
		{
			VR = getVR(stag);//无显示VR时根据tag一个一个去找 真烦啊。
			ST_NUM num;

			num.a[0] = fileData[startPos];
			num.a[1] = fileData[startPos + 1];
			num.a[2] = fileData[startPos + 2];
			num.a[3] = fileData[startPos + 3];
			len = num.v_ui;
			startPos += 4;
		}
		vector<unsigned char>VF;
		if (stag == "7fe0,0010")
		{
			pxDataLen = len;
			pixDataOffset = startPos;
			for (int i = 0; i < len; i++)
			{
				VF.push_back(fileData[startPos]);
				startPos++;
			}
			VR = "UL";
		}
		else if ((VR == "SQ" && len == ST_UINT_MAX) || (stag == "fffe,e000" && len == ST_UINT_MAX))
		{
			if (enDir == false)
			{
				enDir = true;
				floderData.clear();
				flodertag = stag;
			}
			else
			{
				level++;//VF不赋值
			}
		}
		else if ((stag == "fffe,e00d" && len == 0) || (stag == "fffe,e0dd" && len == 0))//文件夹结束标签
		{
			if (enDir == true)
			{
				enDir = false;
			}
			else
			{
				level--;
			}
		}
		else
		{
			for (int i = 0; i < len; i++)
			{
				VF.push_back(fileData[startPos]);
				startPos++;
			}
		}

		string VFStr;
		VFStr = getVF(VR, VF);

		//----------------------------------------------------------------针对特殊的tag的值的处理
		//特别针对文件头信息处理
		if (stag == "0002,0000")
		{
			fileHeaderLen = len;
			fileHeaderOffset = startPos;
		}
		else if (stag == "0002,0010")//传输语法 关系到后面的数据读取
		{
			if (VFStr == "1.2.840.10008.1.2.1\0")
			{
				isLittleEdian = true;
				isExplicitVR = true;
			}
			else if (VFStr == "1.2.840.10008.1.2.2\0")
			{
				isLittleEdian = false;
				isExplicitVR = true;
			}
			else if (VFStr == "1.2.840.10008.1.2\0")
			{
				isLittleEdian = true;
				isExplicitVR = false;
			}

		}
		for (int i = 1; i <= level; i++)
			stag = "--" + stag;
		//------------------------------------数据搜集代码
		if ((VR == "SQ" && len == ST_UINT_MAX) || (stag == "fffe,e000" && len == ST_UINT_MAX) || level > 0)//文件夹标签代码
		{
			for (int i = 0; i < stag.length(); i++)
			{
				floderData.push_back(stag[i]);
			}
			floderData.push_back('(');
			for (int i = 0; i < VR.length(); i++)
			{
				floderData.push_back(VR[i]);
			}
			floderData.push_back(')');
			floderData.push_back(':');
			for (int i = 0; i < VFStr.length(); i++)
			{
				floderData.push_back(VFStr[i]);
			}

		}
		else if (((stag == "fffe,e00d" && len == 0) || (stag == "fffe,e0dd" && len == 0)) && level == 0)//文件夹结束标签
		{
			for (int i = 0; i < stag.length(); i++)
			{
				floderData.push_back(stag[i]);
			}
			floderData.push_back('(');
			for (int i = 0; i < VR.length(); i++)
			{
				floderData.push_back(VR[i]);
			}
			floderData.push_back(')');
			floderData.push_back(':');
			for (int i = 0; i < VFStr.length(); i++)
			{
				floderData.push_back(VFStr[i]);
			}
			string flodertag1 = flodertag + "SQ";
			tags[flodertag1] = floderData.data();

		}
		else
		{
			string fltag = "";
			fltag += '(';
			fltag += VR;
			fltag += ')';
			for (int i = 0; i < VFStr.length(); i++)
			{
				fltag.push_back(VFStr[i]);
			}
			if (stag == "0028,0010")
			{
				printf("hh");
			}
			tags[stag] = fltag;
		}

	}
	return 0;
}

int DicomData::parseFile(string path)
{

	FILE* pf = fopen(path.c_str(), "r");
	if (pf == NULL)
	{
		return -1;
	}
	fseek(pf, 0, SEEK_END);
	long long lsize = ftell(pf);
	if (lsize <= 132)
	{
		fclose(pf);
		return -1;
	}
	fileData = (unsigned char*)malloc(lsize + 1);
	if (fileData == NULL)
	{
		fclose(pf);
		return -1;
	}
	rewind(pf);
	fread((void*)fileData, sizeof(unsigned char), lsize, pf);
	fclose(pf);

	char DicomHead[5];
	for (int i = 128;; i++)
	{
		int curPos = i - 128;
		if (curPos == 4)
		{
			break;
		}
		DicomHead[curPos] = fileData[i];
	}
	DicomHead[4] = '\0';
	if (strcmp(DicomHead, "DICM") != 0)
	{
		return -1;
	}
	int ans = readTags(fileData, lsize);
	if (ans != 0)
	{
		return ans;
	}
	getImage(fileData,this->fileLenth);
}
STImageData DicomData::getImageData(int windowCenter, int windowWidth)
{
	this->windowWidth = windowWidth;
	this->windowCenter = windowCenter;
	getImage(fileData, this->fileLenth);
	return imageData;
}
bool DicomData::getImage(unsigned char* filedata, long fileLength)
{
	int imgNum;
	int dataLen;
	int validLen;

	int rows = atoi(tags["0028,0010"].substr(4).c_str());
	int cols = atoi(tags["0028,0011"].substr(4).c_str());
	int colors = atoi(tags["0028,0002"].substr(4).c_str());
	dataLen = atoi(tags["0028,0100"].substr(4).c_str());
	validLen = atoi(tags["0028,0101"].substr(4).c_str());

	imageData.cols = cols;
	imageData.rows = rows;
	imageData.pixels.clear();
	long reads = 0;
	for (int i = 0; i < cols * rows; i++)
	{
		if (reads >= pxDataLen)
		{
			break;
		}
		int readLen = dataLen / (8 * colors);
		unsigned char* cData = new unsigned char(readLen);
		for (int f = 0; f < readLen; f++)
		{
			cData[f] = fileData[pixDataOffset + reads + f];
		}
		reads += readLen;
		STpixelStruct pix;
		if (colors == 1)
		{
			int grayGDI;
			ST_NUM num;
			num.a[0] = cData[0];
			num.a[1] = cData[1];
			double gray = num.v_us;
			int grayStart = (windowCenter - windowWidth / 2);
			int grayEnd = (windowCenter + windowWidth / 2);

			if (gray < grayStart)
			{
				grayGDI = 0;
			}
			else if (gray > grayEnd)
			{
				grayGDI = 255;
			}
			else {
				grayGDI = (int)((gray - grayStart) * 255 / windowWidth);
			}
			if (grayGDI > 255)
			{
				grayGDI = 255;
			}
			else if (grayGDI < 0)
			{
				grayGDI = 0;
			}

			pix.r = grayGDI;
			pix.g = grayGDI;
			pix.b = grayGDI;

		}
		else if (colors == 3)
		{
			pix.r = cData[0];
			pix.g = cData[1];
			pix.b = cData[2];
		}
		delete cData;
		cData = NULL;
		imageData.pixels.push_back(pix);
	}

	return false;
}
