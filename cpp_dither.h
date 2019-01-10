#if defined _WIN32 || defined __CYGWIN__ || defined __MINGW32__
  #ifdef BUILDING_DLL
    #ifdef __GNUC__
      #define DLL_PUBLIC __attribute__ ((dllexport))
    #else
      #define DLL_PUBLIC __declspec(dllexport) // Note: actually gcc seems to also supports this syntax.
    #endif
  #else
    #ifdef __GNUC__
      #define DLL_PUBLIC __attribute__ ((dllimport))
    #else
      #define DLL_PUBLIC __declspec(dllimport) // Note: actually gcc seems to also supports this syntax.
    #endif
  #endif
  #define DLL_LOCAL
#else
  #if __GNUC__ >= 4
    #define DLL_PUBLIC __attribute__ ((visibility ("default")))
    #define DLL_LOCAL  __attribute__ ((visibility ("hidden")))
  #else
    #define DLL_PUBLIC
    #define DLL_LOCAL
  #endif
#endif
//#define DLL_PUBLIC __declspec(dllexport)

//DLL_PUBLIC double threshIt(double pix, double colors);
extern "C"
{
	//DLL_PUBLIC double get2DArrayMean(vector<vector<double>> pixels);
	DLL_PUBLIC double get2DArrayMean(double** pixels, int rows, int cols);
	//DLL_PUBLIC void getAArray(vector<vector<double>> pixels, vector<vector<double>> &a_array);
	DLL_PUBLIC void getAArray(double** pixels, double** a_array, int rows, int cols);
	DLL_PUBLIC double threshIt(double pix, double colors);
	DLL_PUBLIC int getDoubleIntensity_asInt_andClip(double apix);
	DLL_PUBLIC double GetRandomNumber(uniform_real_distribution<double> unif, default_random_engine &re);
	//DLL_PUBLIC void dither_VarcoBreak(vector<vector<double>> &pixels, double numcolors);
	DLL_PUBLIC void dither_VarcoBreak(double** pixels, int rows, int cols, double numcolors);
	//DLL_PUBLIC void dither_VarcoBlue(vector<vector<double>> &pixels, double numcolors, bool serpentine);
	DLL_PUBLIC void dither_VarcoBlue(double** pixels, int rows, int cols, double numcolors, bool serpentine);
}