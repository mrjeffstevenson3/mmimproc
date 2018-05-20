load dimensionsgood2.txt
filename = "report_title.txt";
fid = fopen (filename, "r");
m_s = fscanf(fid,'%s');
fclose (fid);


fkern = 'plotgood2'; 
    fid = fopen(fkern, 'rb');
    I = fread(fid, 'float');
   fclose(fid);
    typeinfo(I)
clf;
h = figure('Position',[1,1,4000,2048]);
dimensionsgood2
for it = 1:dimensionsgood2(:,4)-1
pos1 = ((it-1)*(dimensionsgood2(:,3)-1))+1;
pos2 = pos1+dimensionsgood2(:,3)-1;
plot(1:1+dimensionsgood2(:,3)-1,I(pos1:pos2));
hold on
end;

load dimensionsbad2.txt

fkern = 'plotbad2'; 
    fid = fopen(fkern, 'rb');
    I = fread(fid, 'float');
   fclose(fid);
    typeinfo(I)
fkern = 'badvolumes2'; 
    fid = fopen(fkern, 'rb');
    Ib = fread(fid, 'float');
   fclose(fid);
    typeinfo(Ib)


dimensionsbad2
map=rainbow(dimensionsbad2(:,4)-1);
for it = 1:dimensionsbad2(:,4)-1
pos1 = ((it-1)*(dimensionsbad2(:,3)-1))+1;
pos2 = pos1+dimensionsbad2(:,3)-1;
[R, G, B] = ind2rgb (it, map);
if (it == 1)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('+-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 2)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('o-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 3)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('s-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 4)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('d-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 5)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('*-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif

if (it == 6)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('x-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 7)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('^-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 8)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('>-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 9)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('<-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 10)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('p-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it == 11)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('h-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif
if (it > 11)
plot(1:1+dimensionsbad2(:,3)-1,I(pos1:pos2),sprintf ('.-;%d;',Ib(it:it)-1), 'Linewidth', 2, 'color',[R, G, B]);
 endif


hold ("on"); 
end;
plot(1:75,(1:75)/10000);
xlabel('slice number ','fontsize',20)
ylabel('Interlace Correlation ','fontsize',20)
title(m_s,'fontsize',20)
set(gca,'fontsize',15);
print('qcreport2.jpg','-djpg',"-S3000,1500");
pause;

