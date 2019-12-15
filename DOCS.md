# run                                                                                                                                                                                                                        
`docker build -t rpg-env .`

`docker run -v $(pwd):/home/jovyan -p 8888:8888 rpg-env`

`main.ipynb`

must open in notebook. widgets not working in lab.

# notebook stylesheet (handled in Dockerfile): 
`!curl https://raw.githubusercontent.com/powerpak/jupyter-dark-theme/master/custom.css -o .jupyter/custom/custom.css`

