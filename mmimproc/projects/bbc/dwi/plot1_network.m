
load brain10.txt
load brain11.txt
load behav1.txt
%% making lines for each mode  %%
h = figure('Position',[1,1,4000,2048]);
plot(behav1,brain10,"@12",'Linewidth', 4,"markersize", 50);
hold on;
r=corr(behav1,brain10)
text(10,20,['correlation r=' num2str(r)],'fontsize',20)
[p,s]=polyfit(behav1,brain10,1);
f=polyval(p,behav1);

plot(behav1,f,'Linewidth', 4,"markersize", 50);
hold on;
plot(behav1,brain11,"@11",'Linewidth', 4,"markersize", 50);
hold on;
r=corr(behav1,brain11)
text(10,20,['correlation r=' num2str(r)],'fontsize',20)
[p,s]=polyfit(behav1,brain11,1);
f=polyval(p,behav1);

plot(behav1,f,'Linewidth', 4,"markersize", 50);

xlabel('behav #25 ','fontsize',20)
ylabel('Foster DTI cluster coefficient ','fontsize',20)
title('correlation','fontsize',20)

print('test.jpg','-djpg',"-S3000,1500");
pause;
