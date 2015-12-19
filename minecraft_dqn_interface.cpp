#include "minecraft_dqn_interface.hpp"

#include <iostream>

Interface::Interface(int argc, char *argv[], std::string path) {
  initInterface(argc, argv, path);
}

Interface::~Interface() {
  Py_Finalize();
}

void Interface::initInterface(int argc, char *argv[], std::string modpath) {
  std::cout << "Initializing" << std::endl;
  char * name = const_cast<char*>("game.py");
  Py_SetProgramName(name);
	Py_Initialize();
	PySys_SetArgv(argc, argv);	
	
	std::string paths[] = {
	   modpath,
	   "/home/trevor/Documents/dev/anaconda2/lib/python27.zip",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/plat-linux2",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/lib-tk",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/lib-old",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/lib-dynload",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/site-packages/Sphinx-1.3.1-py2.7.egg",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/site-packages/setuptools-18.8.1-py2.7.egg",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/site-packages",
	   "/home/trevor/Documents/dev/anaconda2/lib/python2.7/site-packages/cryptography-1.0.2-py2.7-linux-x86_64.egg"
	};
	
	for (int p = 0; p < 11; p++) {
	  std::string path = "import sys\nsys.path.append('" + paths[p] + "')\n";
	  PyRun_SimpleString(path.c_str());
	}
	
	std::cout << "Paths set" << std::endl;
	
  PyObject *pModuleName = PyString_FromString(moduleName);
	module = PyImport_Import(pModuleName);
  if (module != nullptr) {
	  initMethods();
	} else {
	  PyErr_Print(); 
	  exit(1); 
	}
	Py_DECREF(pModuleName);
}


void Interface::initMethods() {
	py_init = PyObject_GetAttrString(module, "init");
  if (!py_init || !PyCallable_Check(py_init)) {
    PyErr_Print();
  }
  
  py_get_action_set = PyObject_GetAttrString(module, "get_action_set");
  if (!py_get_action_set || !PyCallable_Check(py_get_action_set)) {
    PyErr_Print();
  }
  
  py_get_screen = PyObject_GetAttrString(module, "get_screen");
  if (!py_get_screen || !PyCallable_Check(py_get_screen)) {
    PyErr_Print();
  }
  
  py_act = PyObject_GetAttrString(module, "act");
  if (!py_act || !PyCallable_Check(py_act)) {
    PyErr_Print();
  }
  
  py_is_game_over = PyObject_GetAttrString(module, "is_game_over");
  if (!py_is_game_over || !PyCallable_Check(py_is_game_over)) {
    PyErr_Print();
  }
  
	py_reset = PyObject_GetAttrString(module, "reset");
  if (!py_reset || !PyCallable_Check(py_reset)) {
    PyErr_Print();
  }
}


/*
 * Initialize the python game
 */
void Interface::init() {
  std::cout << "initing" << std::endl;
  PyObject *pValue = PyObject_CallObject(py_init, nullptr);
  PyErr_Print();
  if (PyString_Check(pValue)) {
    std::cout << PyString_AsString(pValue) << std::endl;
  }
  Py_DECREF(pValue);
}


/*
 * Get the set of possible actions as a list of integers
 */
std::vector<int> Interface::get_action_set() {
  std::vector<int> actions;

  PyObject *pValue = PyObject_CallObject(py_get_action_set, nullptr);
  if (PyList_Check(pValue)) {
    PyObject *iter = PyObject_GetIter(pValue);
  
    if (iter == nullptr) {
      PyErr_Print();
      exit(1);
    }
    
    PyObject *item;
    while ( (item = PyIter_Next(iter)) ) {
      actions.push_back((int)PyInt_AsLong(item));
      Py_DECREF(item);
    }
    
    Py_DECREF(iter);
  }

  Py_DECREF(pValue);
  
  return actions;
}


/*
 * Update the game state and get the current screen
 * Converts the returned byte array into a cv::Mat
 */

cv::Mat Interface::get_screen() {
  return get_screen(0, 0);
} 
cv::Mat Interface::get_screen(int gitr, int fitr) {
  PyObject *pValue = PyObject_CallObject(py_get_screen, nullptr);
  cv::Mat tmp;
  
  // assuming we have a list
  if (PyList_Check(pValue)) {
    int width = 84, height = 84;
    int channels = 1;
    int i = 0;
    tmp.create(width, height, CV_8UC3);
    for (int r = 0; r < height; r++) {
      for (int c = 0; c < width; c++) {
      
        if (channels == 1) {
          PyObject *v = PyList_GetItem(pValue, i);
          tmp.at<uchar>(r, c) = (uchar)PyInt_AsLong(v);
        } else {         
          PyObject *rd = PyList_GetItem(pValue, i);
          PyObject *gr = PyList_GetItem(pValue, i+1);
          PyObject *bl = PyList_GetItem(pValue, i+2);
          
          //std::cout << "Red: " << (int)PyInt_AsLong(rd) << ", " << 
          //             "Green: " << (int)PyInt_AsLong(gr) << ", " <<
          //             "Blue: " << (int)PyInt_AsLong(bl) << std::endl;

          tmp.at<cv::Vec3b>(r, c) = cv::Vec3b((uchar)PyInt_AsLong(bl),
                                              (uchar)PyInt_AsLong(gr),
                                           	  (uchar)PyInt_AsLong(rd));
        }
                
        i+=channels;
      }
    }    
  }         
  
  cv::Mat screen;
  // flip over the x axis
  cv::flip(tmp, screen, 0);
  
  std::string file = "screens/image" + std::to_string(gitr) + "_" + std::to_string(fitr) + ".png";
  //std::cout << "file = " << file << std::endl;
  cv::imwrite(file, screen);

  Py_DECREF(pValue);
  return screen;
}


/*
 * Perform the action designated by the id
 */
int Interface::act(int action) {
  // parameter must be tuple
  // https://docs.python.org/2.0/ext/buildValue.html
  PyObject *pAction = Py_BuildValue("(i)", action);
  PyObject *pValue = PyObject_CallObject(py_act, pAction);
  int ret = 0;
  if (PyInt_Check(pValue)) {
    ret = (int)PyInt_AsLong(pValue);
  }
  
  Py_DECREF(pAction);
  Py_DECREF(pValue);
  
  return ret;
}


/*
 * Return true if the current game has ended
 */
bool Interface::is_game_over() {
  PyObject *pValue = PyObject_CallObject(py_is_game_over, nullptr);
  bool ret = true;
  if(PyBool_Check(pValue)) {
    ret = (pValue == Py_True); 
  }
  Py_DECREF(pValue);
  return ret;
}


/*
 * Reset the state of the game to the starting state
 */
void Interface::reset() {
  PyObject_CallObject(py_reset, nullptr);
}


int main(int argc, char *argv[]) {
  Interface iface(argc, argv, "");	
  iface.init();
  iface.get_action_set();
  iface.act(0);
  
  int frameItr = 0;
  int gameItr = 0;
  while (gameItr < 2) {
    cv::Mat screen = iface.get_screen(gameItr, frameItr);
    bool over = iface.is_game_over();
    if (over) {
      std::cout << "Finished game " << gameItr << ". Resetting..." << std::endl;
      iface.reset();
      gameItr++;
    }
    frameItr++;
  }
  
  return 0;
}
