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
#define diff(img, x1, y1, x2, y2) pow(img(x1,y1) - img(x2,y2),2)

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

inline int round(double x)
{
	int fl = (int) floor(x);
	if (x-fl > 0.5)
		return fl+1;
	else
		return fl;
}


void compute_sigmas(CImg<double> &image, CImg<double> &sigmas)
{
	int w=image.width;
	int h=image.height;

	for (int i=0; i<w; ++i)
	{
		for (int j=0; j<h; ++j)
		{
			double sum=0;
			int xmax = min(w-1, i+10);
			int ymax = min(h-1, j+10);
			int xmin = max(0,i-10);
			int ymin = max(0,j-10);

			for (int x=xmin; x<xmax; ++x)
			{
				for (int y=ymin; y<ymax; ++y)
				{
					double tmp = image(x,y);

					sum += abs(tmp-image(x+1,y));
					sum += abs(tmp-image(x,y+1));
				}
			}

			sigmas(i,j) = sum / (2*(xmax-xmin)*(ymax-ymin));

		}
	}

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
					  int &nx, double &beta, bool &auto_background, bool &star_shape_prior)
{
	if (auto_background)
		G.add_tweights(y*nx+x, INF, 0);

	if (!star_shape_prior)
		return;

	int dx = (x<X) ? 1 : (-1);
	int dy = (y<Y) ? 1 : (-1);

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

			dx = next_i - i;
			int code = 3*(dx+1) + dy + 1;

			if (!edges_status_out(i,j,code))
			{
				G.add_edge(j*nx + i, next_j*nx + next_i, beta, INF);
				edges_status_out(i, j, code) = true;
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

			dy = next_j - j;
			int code = 3*(dx+1) + dy + 1;

			if (!edges_status_out(i,j, code))
			{
				G.add_edge(j*nx + i, next_j*nx + next_i, beta, INF);
				edges_status_out(i,j, code) = true;	
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



inline void draw_edges_image_data(GraphType &G, CImg<double> &image,
								  int &x1, int &y1, int x2, int y2, int &nx, int &ny,
								  double &lambda, CImg<double> &sigmas, double &sigma_hard, double dist)
{
	if (x2 >= 0 && x2<nx && y2>=0 && y2 < ny)
	{
		double sigma;
		if (sigma_hard != 0)
			sigma = sigma_hard;
		else
			sigma = sigmas(x1, y1);

		double weight = lambda * exp(-diff(image, x1, y1, x2, y2)/(2*sigma*sigma)) / dist;
		if (sigma == 0)
			weight = 0;

		G.add_edge(y1*nx+x1, y2*nx+x2, weight, weight);	//Voisin du haut
	}
}



int main( int argc, char *argv[]  )
{
	CImg<double> image;
	CImg<double> mask;

	//Algo parameters
	double lambda;
	double sigma = 0;
	double beta;

	bool auto_background;
	bool star_shape_prior;
	bool compute_beta = true;

#ifndef TEST
	lambda = atof(argv[1]);
	sigma  = atof(argv[2]);
	beta   = atof(argv[3]);
	if (beta == -234.12)
		compute_beta = true;

	auto_background  = (atof(argv[4]) == 1);
	star_shape_prior = (atof(argv[5]) == 1);

	cout << "Lambda=" << lambda << endl;
	cout << "Sigma=" << sigma << endl;
	if (!compute_beta)
		cout << "Beta=" << beta << endl;
	else
		cout << "Optimal beta search activated" << endl;
	cout << "Auto-Background=" << auto_background << endl;
	cout << "Star Shape=" << star_shape_prior << endl;
#else
	cout << "TEST " << endl << endl;
	//Parameters
	lambda = 20;
	//beta = -20;
	auto_background = true;
	star_shape_prior = true;

#endif

	//Loads images
	image.load("image.bmp");
	//image = image.RGBtoLab();
	mask.load("mask.bmp");
	mask = mask.get_channel(0);

	unsigned int w = image.width;
	unsigned int h = image.height;

	CImg<double> sigmas(w,h);
	if (sigma == 0)
		compute_sigmas(image, sigmas);

#ifdef TEST
	//display_image(sigmas);
	sigmas.save("sigmas.bmp");
#endif

	//Loads object.background seeds
	std::vector<Point> object_points;
	std::vector<Point> background_points;
	find_points(mask, object_points, background_points);

	int X = object_points[0].x;
	int Y = object_points[0].y;

#ifdef TEST
	//Display points coordinates
	cout << "Object points:" << endl;
	for (unsigned int i=0; i<object_points.size(); ++i)
		cout << object_points[i].x << " " << object_points[i].y << endl;
	cout << endl;

	cout << "Background points:" << endl;
	for (unsigned int i=0; i<background_points.size(); ++i)
		cout << background_points[i].x << " " << background_points[i].y << endl;
	cout << endl;

#endif


	//Finding optimal beta
	double beta_min = -30;
	double beta_max = 0;
	int iters_max = 10;

	double beta_sup = beta_max;
	double beta_inf = beta_min;
	if (compute_beta)
		beta = (beta_sup + beta_inf)/2;

	int nb_iters = 0;
	int nx=w, ny=h;	// Sans les bords
	GraphType G(nx*ny,16*nx*ny);

	while (true)
	{
		cout << "Iteration " << nb_iters << endl;
		cout << "Beta=" << beta << endl;

		// Graphe
		cout << "Setting graph...";

		G.reset();
		G.add_node(nx*ny);

		//Data term
		for (int i=0; i<nx; i++)
		{
			for (int j=0; j<ny; j++)
			{
				G.add_tweights(j*nx+i, 0, 0);

				draw_edges_image_data(G, image, i, j, i, j+1, nx, ny, lambda, sigmas, sigma, 1);	//Down
				draw_edges_image_data(G, image, i, j, i+1, j, nx, ny, lambda, sigmas, sigma, 1);	//Right
				draw_edges_image_data(G, image, i, j, i+1, j-1, nx, ny, lambda, sigmas, sigma, sqrt(2.));	//Top right
				draw_edges_image_data(G, image, i, j, i+1, j+1, nx, ny, lambda, sigmas, sigma, sqrt(2.));	//Down right

			}
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



		//Star shape edges
		CImg<bool> edges_status_out(w, h, 9, 1, false);
		int x, y;
		for (unsigned int i=0; i<w; ++i)
		{
			x = i;
			y = 0;
			draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background, star_shape_prior);

			x = i;
			y = image.height - 1;
			draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background, star_shape_prior);
		}
		for (unsigned int j=1; j<h-1; ++j)
		{
			x = 0;
			y = j;
			draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background, star_shape_prior);

			x = image.width - 1;
			y = j;
			draw_line(edges_status_out, G, x, y, X, Y, nx, beta, auto_background, star_shape_prior);
		}
		cout << "Done." << endl;

		// Coupe
		cout << "Computing Cut..." << endl;
		double f = G.maxflow();
		cout << f << endl;

		if (!compute_beta)
			break;


		// Segmentation result
		int nb_objects=0;
		for (int j=0;j<ny;j++) {
			for (int i=0;i<nx;i++) {
				if (G.what_segment(j*nx+i)==GraphType::SINK)
					nb_objects++;
			}
		}
		cout << "Object contains " << nb_objects << " points" << endl << endl;

		//New beta
		if (nb_objects < 100)
		{
			//On baisse le beta
			beta_inf = beta_inf;
			beta_sup = beta;
			beta = (beta_inf + beta)/2;

			if (beta - beta_min < 0.05)
			{
				cout << "Diminution du beta..." << endl;
				beta_inf -= 50;
				beta_min = beta_inf;
				beta_sup = beta;
				beta = (beta_inf + beta)/2;
				nb_iters = 0;
			}
		}
		else
		{
			if (nb_iters >= iters_max)
				break;

			//On augmente le beta
			beta_inf = beta;
			beta_sup = beta_sup;
			beta = (beta_sup + beta)/2;

			if (beta_max - beta < 0.05)
			{
				cout << "augmentation du beta..." << endl;
				beta_sup += 50;
				beta_max = beta_sup;
				beta_inf = beta;
				beta = (beta_sup + beta)/2;
				nb_iters = 0;
			}
		}

		nb_iters++;
	}



	// Dessin de la zone objet
	for (int j=0;j<ny;j++) {
		for (int i=0;i<nx;i++) {
			if (G.what_segment(j*nx+i)==GraphType::SINK)
			{
				image(i,j,0) = 0;
				image(i,j,1) = 255;
				image(i,j,2) = 0;
			}
		}
	}

	//Dessin object points
	for (unsigned int in=0; in<object_points.size(); ++in)
	{
		for (int i=-2; i<=2; ++i)
		{
			for (int j=-2; j<=2; ++j)
			{
				image(object_points[in].x+i, object_points[in].y+j, 0) = 255;
				image(object_points[in].x+i, object_points[in].y+j, 1) = 255;
				image(object_points[in].x+i, object_points[in].y+j, 2) = 0;
			}
		}
	}

	//Dessin background points
	for (unsigned int in=0; in<background_points.size(); ++in)
	{
		for (int i=-2; i<=2; ++i)
		{
			for (int j=-2; j<=2; ++j)
			{
				image(background_points[in].x+i, background_points[in].y+j, 0) = 0;
				image(background_points[in].x+i, background_points[in].y+j, 1) = 255;
				image(background_points[in].x+i, background_points[in].y+j, 2) = 255;
			}
		}
	}



#ifdef TEST
	display_image(image);
#endif

	image.save("results.bmp");

	return 0;
}
