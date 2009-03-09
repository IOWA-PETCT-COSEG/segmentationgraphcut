#include "maxflow/graph.h"
#include "point.h"

#include <iostream>
#include <fstream>

#include <math.h>
#include <vector>

#include "CImg.h"

using namespace cimg_library;
using namespace std;


//#define TEST
#define INF 100000000
#define diff(img, x1, y1, x2, y2) (pow(img(x1,y1,0) - img(x2,y2,0),2)+pow(img(x1,y1,1) - img(x2,y2,1),2)+pow(img(x1,y1,2) - img(x2,y2,2),2))

typedef Graph<double,double,double> GraphType;

/**
* Affiche de l'image à l'écran
**/
template <class T> 
void display_image(CImg<T> &image)
{
	CImgDisplay display(image, "Image");
	display.wait();
}

inline int round(double x) {
	int fl = (int) floor(x);
	if (x-fl > 0.5)
		return fl+1;
	else
		return fl;
}





/**
* Find object points and background points in the mask image
**/
void find_points(CImg<double> &mask,
				 std::vector<Point> &object_points,
				 std::vector<Point> &background_points)
{
	for (unsigned int i=0; i<mask.width; ++i)
	{
		for (unsigned int j=0; j<mask.height; ++j)
		{
			double val = mask(i,j);
			if (val == 1)
				object_points.push_back(Point(i,j));
			else if (val == 0)
				background_points.push_back(Point(i,j));
		}
	}
}


/**
* Set edges correponding to a line starting from the border of the image to the star point
**/
inline void draw_line(CImg<bool> &edges_status_out, GraphType &G,
			   int &x, int &y, int &X, int &Y,
			   int &nx, double &beta, bool &auto_background)
{
	int dx = (x<X) ? 1 : (-1);
	int dy = (y<Y) ? 1 : (-1);

	if (auto_background)
		G.add_tweights(y*nx+x, INF, 0);

	//Current point: (i,j)
	int i,j;

	if (abs(Y-y) > abs(X-x))
	{
		double slopey = 1.*(X-x)/(Y-y);
		//Parcours en y
		//cout << "Parcours en y" << endl;
		for (int j=y; j != Y; j+=dy)
		{
			i = round((j-y)*slopey + x);

			//Next point: ((j+dy-y)*slopey + x, j+dy)
			int next_i = round((j+dy-y)*slopey + x);
			int next_j = j+dy;

			if (!edges_status_out(i,j))
			{
				G.add_edge(j*nx + i, next_j*nx + next_i, beta, INF);
				edges_status_out(i, j) = true;
			}
		}
	}
	else
	{
		//Parcours en x
		//cout << "Parcours en x" << endl;
		double slopex = 1.*(Y-y)/(X-x);

		for (int i=x; i != X; i+=dx)
		{
			j = round(slopex * (i-x) + y);

			//Next point: (i+dx, slope * (i+dx-x) + y)
			int next_i = i+dx;
			int next_j = round(slopex * (i+dx-x) + y);

			if (!edges_status_out(i,j))
			{
				G.add_edge(j*nx + i, next_j*nx + next_i, beta, INF);
				edges_status_out(i,j) = true;	
			}


		}
	}
	//if (x==780 && y%10==0)
	//{
	//	cout << y << endl;
	//CImgDisplay display(edges_status_out, "edges_status_out");
	//display.wait(100);
	//}
	//edges_status_out.save("lol.bmp");
}










int main( int argc, char *argv[]  )
{

	CImg<double> image;
	CImg<double> mask;

	//Algo parameters
	double lambda;
	double sigma;
	double beta;
	bool auto_background;

#ifndef TEST
	lambda = atof(argv[1]);
	sigma  = atof(argv[2]);
	beta   = atof(argv[3]);

	auto_background = (atof(argv[4]) == 1);

	cout << "Lambda=" << lambda << endl;
	cout << "Sigma=" << sigma << endl;
	cout << "Beta=" << beta << endl;
	cout << "Auto-Background=" << auto_background << endl;
#else
	cout << "TEST " << endl << endl;
	//Parameters
	lambda = 10000000;
	sigma = 3;
	beta = 10;
	auto_background = true;
#endif

	//Loads images
	image.load("image.bmp");
	mask.load("mask.bmp");
	mask = mask.get_channel(0);

	unsigned int w = image.width;
	unsigned int h = image.height;

	//Loads object.background seeds
	std::vector<Point> object_points;
	std::vector<Point> background_points;
	find_points(mask, object_points, background_points);

	int X = object_points[0].x;
	int Y = object_points[0].y;

#ifdef TEST
	//Display points coordinates
	cout << "Object points:" << endl;
	for (int i=0; i<object_points.size(); ++i)
		cout << object_points[i].x << " " << object_points[i].y << endl;
	cout << endl;

	cout << "Background points:" << endl;
	for (int i=0; i<background_points.size(); ++i)
		cout << background_points[i].x << " " << background_points[i].y << endl;
	cout << endl;
#endif

	// Graphe
	cout << "Setting graph" << endl;
	int nx=w, ny=h;	// Sans les bords

	CImg<bool> edges_status_out(w, h, 1, 1, false);

	GraphType G(nx*ny*2,2*nx*ny*4);
	G.add_node(nx*ny);

	for (int j=0; j<ny; j++)
	{
		for (int i=0; i<nx; i++)
		{
			double weight;

			//Voisins
			if (j-1 >= 0 && j-1 < ny)
			{
				weight = lambda * exp(-diff(image, i, j, i, j-1)/(2*sigma*sigma));
				G.add_edge(j*nx+i, (j-1)*nx+i, weight, weight);	//Voisin du haut
			}
			if (j+1 >= 0 && j+1 < ny)
			{
				weight = lambda * exp(-diff(image, i, j, i, j+1)/(2*sigma*sigma));
				G.add_edge(j*nx+i, (j+1)*nx+i, weight, weight);	//Voisin du bas
			}
			if (i-1 >= 0 && i-1 < nx)
			{
				weight = lambda * exp(-diff(image, i, j, i-1, j)/(2*sigma*sigma));
				G.add_edge(j*nx+i, j*nx+i-1, weight, weight);	//Voisin de gauche
			}
			if (i+1 >= 0 && i+1 < nx)
			{
				weight = lambda * exp(-diff(image, i, j, i+1, j)/(2*sigma*sigma));
				G.add_edge(j*nx+i, j*nx+i+1, weight, weight);	//Voisin de droite
			}

		}
	}

	//Star shape edges
	int x, y;
	for (unsigned int i=0; i<w; ++i)
	{
		x = i;
		y = 0;
		draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background);

		x = i;
		y = image.height - 1;
		draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background);
	}
	for (unsigned int j=1; j<h-1; ++j)
	{
		x = 0;
		y = j;
		draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background);

		x = image.width - 1;
		y = j;
		draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background);
	}



	//Seed object points
	for (unsigned int i=0; i<object_points.size(); ++i)
	{
		int x = object_points[i].x;
		int y = object_points[i].y;
		G.add_tweights(y*nx+x, 0, INF);
	}

	//Background object points
	for (unsigned int i=0; i<background_points.size(); ++i)
	{
		int x = background_points[i].x;
		int y = background_points[i].y;
		G.add_tweights(y*nx+x, INF, 0);
	}



	// Coupe
	cout << "Computing Cut" << endl;
	double f = G.maxflow();
	cout << f << endl;

	// Segmentation result
	int nb_objects=0;
	CImg<int> D(nx,ny);
	for (int j=0;j<ny;j++) {
		for (int i=0;i<nx;i++) {
			int disp = 0;
			if (G.what_segment(j*nx+i)==GraphType::SINK)
			{
				disp = 255;
				nb_objects++;
				image(i,j,1) = 255;
			}

			D(i,j)=disp;

		}
	}

	//Dessin du seed point
	for (int i=-2; i<=2; ++i)
		for (int j=-2; j<=2; ++j)
			image(X+i, Y+j, 2) = 255;


	//cout << "Segmentation results:" << endl;
	//cout << "Object" << endl;
	////Seed object points
	//for (int i=0; i<object_points.size(); ++i)
	//	cout << D(object_points[i].x, object_points[i].y) << endl;
	//cout << endl;

	//cout << "Background" << endl;
	////Background object points
	//for (int i=0; i<background_points.size(); ++i)
	//	cout << D(background_points[i].x, background_points[i].y) << endl;
	//cout << endl;

	cout << "Object contains " << nb_objects << " points" << endl;
#ifdef TEST
	display_image(image);
#endif

	image.save("results.bmp");

	return 0;
}
