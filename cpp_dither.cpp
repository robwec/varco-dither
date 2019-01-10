#include <iostream>
#include <vector>
using namespace std;
#include "varco.cpp"
//#include <iomanip> //setprecision
#include <algorithm> //min, max
#include <random> //random
#include "cpp_dither.h"

//double get2DArrayMean(vector<vector<double>> pixels)
double get2DArrayMean(double** pixels, int rows, int cols)
{
	//int rows = pixels.size();
	//int cols = pixels[0].size();
	double sum = 0.;
	int row, col;
	for (row = 0; row < rows; row++)
	{
		for (col = 0; col < cols; col++)
		{
			sum += pixels[row][col];
		}
	}
	double cells = rows*cols;
	double mean = sum / cells;
	return mean;
}
//void getAArray(vector<vector<double>> pixels, vector<vector<double>> &a_array)
void getAArray(double** pixels, double** a_array, int rows, int cols)
{
	//int rows = pixels.size();
	//int cols = pixels[0].size();
	double g_prime = 0.;
	int row, col;
	for (row = 0; row < rows; row++)
	{
		for (col = 0; col < cols; col++)
		{
			g_prime = abs(1 - 2*pixels[row][col]);
			a_array[row][col] = pow(1 - g_prime, 2) * (1 + 2*g_prime);
		}
	}
	return;
}
double threshIt(double pix, double colors)
{
	double inverse_thingy = 1. / (colors - 1.);
	double sol = round(pix / inverse_thingy) * inverse_thingy;
	sol = max(0., min(1., sol));
	return sol;
}
int getDoubleIntensity_asInt_andClip(double apix)
{
	int int_intensity = (int) round(apix * (double) 255);
	int_intensity = (int) max(0, (int) min(int_intensity, (int) 255));
	return int_intensity;
}
double GetRandomNumber(uniform_real_distribution<double> unif, default_random_engine &re)
{
	return unif(re);
}
//
//
//void dither_VarcoBreak(vector<vector<double>> &pixels, double numcolors)
void dither_VarcoBreak(double** pixels, int rows, int cols, double numcolors)
{
	double mean_intensity = get2DArrayMean(pixels, rows, cols);
	mean_intensity = max(1., 255.*mean_intensity); //max to prevent divide by 0.
	double epsilon = pow(1./mean_intensity, 2.);
	//using this to determine how much to randomize each pixel
	//vector<vector<double>> a_array(pixels);
	//double** a_array(pixels);
	double** a_array = new double*[rows];
	for (int i=0; i < rows; i++)
	{
		a_array[i] = new double[cols];
		for (int j=0; j < cols; j++)
		{
			a_array[i][j] = 0.;
		}
	}
	//getAArray(pixels, a_array);
	getAArray(pixels, a_array, rows, cols);
	//
	int row, col;
	//int rows = pixels.size();
	//int cols = pixels[0].size();
	double oldpix, newpix, error;
	double varcoweights[256][3] = {0.};
	create_varcoWeightsList_double(varcoweights);
	int oldpixintensity;
	double thisweight_1, thisweight_2, thisweight_3;
	double xi_1, this_a, newsum;
	double xi_2;
	uniform_real_distribution<double> unif(-1.0, 1.0);
	//default_random_engine re; //is always the same?
	random_device rd;
	default_random_engine re(rd()); //how about this?
	for (row = 0; row < rows; row++)
	{
		for (col = 0; col < cols; col++)
		{
			oldpix = pixels[row][col];
			pixels[row][col] = threshIt(oldpix, numcolors);
			newpix = pixels[row][col];
			error = oldpix - newpix;
			//
			oldpixintensity = getDoubleIntensity_asInt_andClip(oldpix);
			thisweight_1 = varcoweights[oldpixintensity][0];
			thisweight_2 = varcoweights[oldpixintensity][1];
			thisweight_3 = varcoweights[oldpixintensity][2];
			if (true)
			{
				xi_1 = GetRandomNumber(unif, re);
				xi_2 = GetRandomNumber(unif, re);
				this_a = a_array[row][col];
				//
				thisweight_1 = thisweight_1*(1 + this_a*xi_1); //right
				thisweight_2 = thisweight_2*(1 - this_a*xi_2); //down-left
				thisweight_3 = thisweight_3*(1 + this_a*xi_2); //down
			}
			//
			newsum = thisweight_1 + thisweight_2 + thisweight_3;
			if (newsum == 0)
			{
				newsum = 1;
			}
			thisweight_1 /= newsum;
			thisweight_2 /= newsum;
			thisweight_3 /= newsum;
			if (col + 1 < cols && col + 1 >= 0)
			{
				pixels[row][col + 1] += thisweight_1 * error;
			}
			if ((col - 1 < cols && col - 1 >= 0) && (row + 1 < rows && row + 1 >= 0))
			{
				pixels[row + 1][col - 1] += thisweight_2 * error;
			}
			if (row + 1 < rows && row + 1 >= 0)
			{
				pixels[row + 1][col] += thisweight_3 * error;
			}
		}
	}
	return;
}
//
//void dither_VarcoBlue(vector<vector<double>> &pixels, double numcolors, bool serpentine)
void dither_VarcoBlue(double** pixels, int rows, int cols, double numcolors, bool serpentine)
//void dither_VarcoBlue(double **pixels[rows][cols], double numcolors, bool serpentine)
{
	int row, col;
	//int rows = pixels.size();
	//int cols = pixels[0].size();
	double oldpix, newpix, error;
	double varcoweights[256][3] = {0.};
	create_varcoWeightsList_double(varcoweights);
	int oldpixintensity;
	for (row = 0; row < rows; row++)
	{
		if (serpentine && (row % 2) == 1)
		{
			for (col = cols - 1; col >= 0; col--)
			{
				oldpix = pixels[row][col];
				oldpixintensity = getDoubleIntensity_asInt_andClip(oldpix);
				pixels[row][col] = threshIt(oldpix, numcolors);
				newpix = pixels[row][col];
				error = oldpix - newpix;
				if (col - 1 < cols && col - 1 >= 0)
				{
					pixels[row][col - 1] += varcoweights[oldpixintensity][0] * error;
				}
				if ((col + 1 < cols && col + 1 >= 0) && (row + 1 < rows && row + 1 >= 0))
				{
					pixels[row + 1][col + 1] += varcoweights[oldpixintensity][1]* error;
				}
				if (row + 1 < rows && row + 1 >= 0)
				{
					pixels[row + 1][col] += varcoweights[oldpixintensity][2] * error;
				}
			}
		}
		else
		{
			for (col = 0; col < cols; col++)
			{
				oldpix = pixels[row][col];
				oldpixintensity = getDoubleIntensity_asInt_andClip(oldpix);
				pixels[row][col] = threshIt(oldpix, numcolors);
				newpix = pixels[row][col];
				error = oldpix - newpix;
				if (col + 1 < cols && col + 1 >= 0)
				{
					pixels[row][col + 1] += varcoweights[oldpixintensity][0] * error;
				}
				if ((col - 1 < cols && col - 1 >= 0) && (row + 1 < rows && row + 1 >= 0))
				{
					pixels[row + 1][col - 1] += varcoweights[oldpixintensity][1]* error;
				}
				if (row + 1 < rows && row + 1 >= 0)
				{
					pixels[row + 1][col] += varcoweights[oldpixintensity][2] * error;
				}
			}
		}
	}
	return;
}