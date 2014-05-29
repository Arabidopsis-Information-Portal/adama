FROM common
ENV HOME /root
RUN apt-get install python

EXPOSE 22

CMD ["/sbin/my_init", "--", "python"]