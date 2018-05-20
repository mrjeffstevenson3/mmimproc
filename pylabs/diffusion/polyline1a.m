load poly1.txt
load poly2.txt
load poly3.txt
load polynum.txt
load polytot.txt
figure('Position',[2,2,1700,900]);
pos1=1;
for j = 1:polytot(1:1)
pos2 = floor(pos1+(polynum(j:j))-1);

%printf('%d \n',pos1)
%printf('%d \n',pos2)
plot(poly2(pos1:pos2),poly3(pos1:pos2));
pos1=pos2+1;
hold on
end;
pause;

