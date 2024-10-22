FROM tiangolo/nginx-rtmp

COPY src/nginx.conf /etc/nginx/nginx.conf

EXPOSE 1935

CMD ["nginx", "-g", "daemon off;"]