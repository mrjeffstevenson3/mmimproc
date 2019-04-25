filename = 'roi.csv';
fname = 'column10.txt';
delimiterIn = ',';
headerlinesIn = 1;
A = importdata(filename,delimiterIn,headerlinesIn);
name = textread("name1.txt","%s",11);
brain10 = textread("brain10.txt","%s",1);
brain11 = textread("brain11.txt","%s",1);
for k = [1:11]
   disp(A.colheaders{1, k})
   disp(A.data(:, k))
   disp(' ')
end
groups=A.data(:,1);
vocabulary=A.data(:,3);
AD=A.data(:,4);
brain10
brain11

ctrl=groups==1;
exp=groups==0;


%% making lines for each mode  %%
h = figure('Position',[1,1,4000,2048]);
map=rainbow(12);
for k = [4:9]
AD=A.data(:,k);
header=A.colheaders{1, k};
[p,s]=polyfit(vocabulary(ctrl),AD(ctrl),1);
diff1=max(vocabulary(ctrl))-min(vocabulary(ctrl));
diff2=max(AD(ctrl))-min(AD(ctrl));
X_axis=[min(vocabulary(ctrl)) max(vocabulary(ctrl))];
Y_axis=[min(AD(ctrl)) max(AD(ctrl))];
f=polyval(p,X_axis);
[R, G, B] = ind2rgb (k-3, map);
plot(X_axis,f,sprintf ('-;%s;',A.colheaders{1, k}),'Linewidth', 4, 'color',[R, G, B],"markersize", 50);
r=corr(vocabulary(ctrl),AD(ctrl))
text(10,(k*4)+50,['correlation r=' num2str(r)],'Color',[R, G, B],'fontsize',20)
text(20+20,(k*4)+50,sprintf (';%s;',A.colheaders{1, k}),'Color',[R, G, B],'fontsize',20)
text(20+30,(k*4)+50,"Control",'Color',[R, G, B],'fontsize',20)


hold on;
end;
for k = [4:9]
AD=A.data(:,k);
header=A.colheaders{1, k};
k
header
[p,s]=polyfit(vocabulary(exp),AD(exp),1);
diff1=max(vocabulary(exp))-min(vocabulary(exp));
diff2=max(AD(ctrl))-min(AD(ctrl));
X_axis=[min(vocabulary(exp)) max(vocabulary(exp))];
Y_axis=[min(AD(exp)) max(AD(exp))];
f=polyval(p,X_axis);
[R, G, B] = ind2rgb (k+4, map);
plot(X_axis,f,sprintf ('-;%s;',A.colheaders{1, k}),'Linewidth', 4, 'color',[R, G, B],"markersize", 50);
r=corr(vocabulary(exp),AD(exp))
text(10,(k*4),['correlation r=', num2str(r)],'Color',[R, G, B],'fontsize',20)
text(20+20,(k*4),sprintf (';%s;',A.colheaders{1, k}),'Color',[R, G, B],'fontsize',20)
text(20+30,(k*4),"Foster",'Color',[R, G, B],'fontsize',20)

hold on;
end;
axis([1 150 1 110])
xlabel(A.colheaders{1, 3},'fontsize',26)
ylabel('DTI','fontsize',26)
title (sprintf ('%s',name{1,1}),'fontsize',20);
text(20,100,sprintf ('brainregion;%s;',brain10{1, 1}),'Color',[R, G, B],'fontsize',20)
text(20,95,sprintf ('brainregion;%s;',brain11{1, 1}),'Color',[R, G, B],'fontsize',20)
print(sprintf ('%s.jpg',name{1,1}),'-djpg',"-S3000,1500");
pause;
