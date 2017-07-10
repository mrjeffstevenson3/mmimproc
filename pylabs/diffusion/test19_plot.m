
load polynum.txt
load polytot.txt
load test19.txt
figure('Position',[2,2,1700,900]);
test19(1,1)
pos1=1;
pos1
pos2=test19(1,1);
pos2
for j = 1:100
plot3(test19(pos1+1:pos2,1),test19(pos1+1:pos2,2),test19(pos1+1:pos2,3));

pos1 = pos1+test19(pos1:pos1,1);
pos1=pos1;
pos1
pos2 = pos1+test19(pos1:pos1,1)-1;
pos2
hold on
end;
pause;

