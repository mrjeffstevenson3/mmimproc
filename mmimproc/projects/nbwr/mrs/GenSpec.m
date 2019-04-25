h = figure ;
load output_correlation.txt
load output_correlation_stats.txt
xdata = output_correlation(:,1); 
ydata = output_correlation(:,2); 
tvalue = output_correlation_stats(1,1); 
probvalue = output_correlation_stats(2,1); 
order = 1; 
p = polyfit (xdata, ydata, order); 
x = linspace (min(xdata), max(xdata), 101); 
y = polyval (p, x); 
plot (x, y, '-', xdata, ydata, 's', "markersize", 8); 
xlabel(' csfcorrected_right-Glu-80ms              ','fontsize',20); 
ylabel(' FSIQ-4_Composite                         ','fontsize',20); 
maxy=max(ydata); 
miny=min(ydata); 
pos1y=miny- ((maxy-miny)*0.1); 
pos2y=maxy+ ((maxy-miny)*0.1); 
maxx=max(xdata); 
minx=min(xdata); 
pos1x=minx- ((maxx-minx)*0.1); 
pos2x=maxx+ ((maxx-minx)*0.1); 
set(gca,'fontsize',15); 
axis([pos1x, pos2x, pos1y,pos2y]); 
title ('MRS/Behavioral correlation', 'fontsize',20);  
rcorr=corr (xdata, ydata); 
rcorr 
str=sprintf("correlation r %f ",rcorr);  
posx_stats=pos1x+((maxx-minx)*0.1); 
posy_stats1=maxy-((maxx-minx)*0.1); 
posy_stats1=maxy-((maxx-minx)*0.15); 
posy_stats1=maxy-((maxx-minx)*0.2); 
text(posx_stats,posy_stats1,str,'fontsize',15); 
str=sprintf("tvalue from rcorr %f ",tvalue);  
text(posx_stats,132,str,'fontsize',15); 
str=sprintf("prob value %f ",probvalue);  
text(posx_stats,134,str,'fontsize',15); 
for it = 1:12  
str=sprintf("%04d ",output_correlation(it,3));  
text(output_correlation(it,1),output_correlation(it,2),str,'fontsize',10); 
end;  
print -djpg 'mrsbehav.jpg' ; 
pause; 
