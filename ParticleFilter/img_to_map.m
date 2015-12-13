% img = imread('marked.png');

% Define constant bit map values.
VOID_SPACE = 0;
HALLWAY = 1;
STAIRCASE = 2;
ELEVATOR = 3;
DOOR = 4;
SITTING_AREA = 5;
STANDING_AREA = 6;

R = 1;
G = 2;
B = 3;

[h, w, ~] = size(img);
bitmap = zeros(h, w);

for r = 1 : h
    for c = 1 : w
        pix = img(r, c, :);
        pix = pix(:);
        if pix(R) > 200 && pix(B) > 200 % purple = sitting area
        	bitmap(r, c) = SITTING_AREA;
        elseif pix(R) > 200 && pix(G) > 200 % yellow = standing area
        	bitmap(r, c) = STANDING_AREA;
        elseif pix(G) > 200 && pix(B) > 200 % cyan = door
            bitmap(r, c) = DOOR;
        elseif pix(R) > 200 % red = stairs
            bitmap(r, c) = STAIRCASE;
        elseif pix(G) > 200 % green = elevator
            bitmap(r, c) = ELEVATOR;
        elseif pix(B) > 200 % blue = hallway
            bitmap(r, c) = HALLWAY;
        end
        % Otherwise, keep it 0 (as a null area)
    end
end

clear h w;

subplot(2, 1, 1);
imshow(img);
subplot(2, 1, 2);
imshow(uint8(bitmap * 40));

% dlmwrite('out.txt', bitmap);