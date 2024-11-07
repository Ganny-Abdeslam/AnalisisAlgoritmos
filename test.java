//Tabulacion

public int sumatoria(int n, int arreglo[]){
    
    arreglo [0] = 0;

    for (int i=1; i<=n; i++){
        arreglo[i] = arreglo[i-1] + i;
    }

    return arreglo[n];
}

//Memorizacion
// 0 1 2 3 4 5 
// 0 1 3 6 10 15 

public int sumatoria(int n, int arreglo[]){
    
    if (n == 0) {
        arreglo[n] = 0;

    }

    else {
        arreglo[n] = n + sumatoria(n-1, arreglo) ;
    }
    return arreglo[n];
}


///////////////////////////////////////////////////////////////////////////////Lucas

//Tabulacion

public int lucas (int n, int arreglo[]){

    arreglo[0] = 2;
    arreglo[1] = 1;

    for (int i = 2; i < n; i++){
        arreglo[i] = arreglo[i-1] + arreglo[i-2];
    }

    return arreglo[n];

}

//Memorizacion

public int lucas (int n, int arreglo[]){

    if (n == 0){
        arreglo[n] = 2;
    }

    if (n == 1){
        arreglo[n] = 1;
    }

    else {
        arreglo[n] = lucas(n-1, arreglo) + lucas(n-2, arreglo);
    }

    return arreglo[n];
}


////////////////////////////////////////////////////////////////// 

///Tabulacion

public int test (int n,int k, int matriz[][]){

    for (int i = 0; i <= n; i++){
        matriz[i][0] = 4;
    }

    for (int i = 0; i <= n; i++){
        for (int j = 0; j <= n; j++){
            
            if ( i == j ){
                matriz[i][j] = Math.pow(i, j) + 3;
            }   
        }   
            
    }

    for (int i = 2; i <= n; i++){
        for (int j = 1; j <= n; j++){
            
            if ( i != j){
                matriz[i][j] = 5*matriz[i-1][j-1] + 3*matriz[i-1][j] - 1;
            }   
        }   
            
    }

    return matriz[n][k];

}

////////////////////////////////////////////////////////////////// TRIANGULO DE PASCAL ////////////////////////////////////////////////////////////////// 

public int[][] misterio (int n, int k)
	{
		int resultado [][] = new int[n+1][k+1];
		
		for (int i = 0; i <= n; i++)
		{
			for (int j = 0; j <= menor(i, k); j++)
			{
				if (j == 0)
				{
					resultado[i][j] = i + j ;
				}
				if (j == i)
				{
					resultado[i][j] = (int) Math.pow(i, j);
				}
				else
				{
					resultado[i][j] = (3*resultado[i-1][j]) + 
      (2*resultado[i-1][j-1])+1 ;
				}
			}
		}
		return resultado;
	}


////////////////////////////////////////////////////////////////// BUSQUEDA BINARIA ////////////////////////////////////////////////////////////////// 

//Recursiva

boolean binRecursiva (int a[], int dato, int limInf, int limSup) {
    
    int centro = (int)( (limSup + limInf) / 2);
    if ( limInf > limSup ) {
        return false;
    }
    else{
        if ( a[ centro ] > dato ){
            return binRecursiva(a, dato, limInf, centro-1 );
        }
        else{
            if (a[centro]<dato){
                return binRecursiva(a,dato,centro+1,limSup );
            }
            else{
                return true;
            }
        }
    }
}

//Iterativa

boolean binIterativa(int a[], int dato, int limInf, int limSup) {
    while (limInf <= limSup) {
        int centro = (limInf + limSup) / 2;

        if (a[centro] == dato) {
            return true; 
        } else if (a[centro] > dato) {
            limSup = centro - 1; 
        } else {
            limInf = centro + 1; 
        }
    }

    return false; // No se encontró el elemento
}



////////////////////////////////////////////////////////////////// Memorizacion //////////////////////////////////////////////////////////////////

public int [][] metodo (int n, int k, int matriz [][]){

    if (k == 0){
        matriz[n][k] = 4;
    }
    if (k == n){
        matriz[n][k] = (int) Math.pow(n, k) + 3;
    }
    else {
        matriz[n][k] = 4*metodo(n, k, matriz[n-1][k-1]) + 3*metodo(n, k, matriz[n-1][k-1]) - 1;
    }
    return matriz [n][k];

}