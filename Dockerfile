FROM paf-depend

WORKDIR /

RUN apt-get update && apt-get install -y --no-install-recommends gnuplot && apt-get clean && updatedb && \
    wget https://repo.continuum.io/archive/Anaconda2-5.0.1-Linux-x86_64.sh -O conda.sh && \ 
    wget https://sourceforge.net/projects/gnuplot-py/files/Gnuplot-py/1.8/gnuplot-py-1.8.tar.gz && \
    tar -xvf gnuplot-py-1.8.tar.gz && \
    bash ./conda.sh -b -p /anaconda2 && rm conda.sh && rm gnuplot-py-1.8.tar.gz

ENV PATH /anaconda2/bin:${PATH}

#Installs GNUPLOT.py
RUN pip install pika && cd gnuplot-py-1.8 && /anaconda2/bin/python2.7 setup.py install

WORKDIR /

#RUN git clone https://git.code.sf.net/p/heimdall-astro/code heimdall

COPY heimdall-quick-fix /heimdall

WORKDIR /heimdall
ENV CUDA_NVCC_FLAGS="-default-stream per-thread"
RUN ./bootstrap && \
    ./configure --prefix=/heimdall-install/ --with-dedisp-include-dir=/dedisp/src/ --with-cuda-dir=/usr/local/cuda-8.0 --with-psrdada-include-dir=/psrdada-install/include/ && \
    make && \
    make install

COPY pika_heimdall_wrapper.py /heimdall/Scripts 

ENTRYPOINT ["python", "Scripts/pika_heimdall_wrapper.py"]