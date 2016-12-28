
load polynum.txt
load polytot.txt
load testchannel.txt
figure('Position',[2,2,1700,900]);
testchannel(1:1)
pos1=2;
pos1
pos2=testchannel(2:2);
pos2
for j = 1:testchannel(1:1)-1
plot(testchannel(pos1+1:pos2));

pos1 = pos1+testchannel(pos1:pos1);
pos1=pos1+1;
pos1
pos2 = pos1+testchannel(pos1:pos1);
pos2
hold on
end;
pause;

