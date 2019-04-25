
load polynum.txt
load polytot.txt
load testbelow_beltline.txt
figure('Position',[2,2,1700,900]);
testbelow_beltline(1,1)
pos1=1;
pos1
pos2=testbelow_beltline(1,1);
pos2
for j = 1:100
plot3(testbelow_beltline(pos1+1:pos2,1),testbelow_beltline(pos1+1:pos2,2),testbelow_beltline(pos1+1:pos2,3));

pos1 = pos1+testbelow_beltline(pos1:pos1,1);
pos1=pos1;
pos1
pos2 = pos1+testbelow_beltline(pos1:pos1,1)-1;
pos2
hold on
end;
pause;

