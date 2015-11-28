% Define constant bit map values.
VOID_SPACE = 0;
HALLWAY = 1;
STAIRCASE = 2;
ELEVATOR = 3;
DOOR = 4;
SITTING_AREA = 5;

[h, w, ~] = size(img);
bitmap = zeros(h, w);

for r = 1 : h
    for c = 1 : w
        pix = img(r, c, :);
        pix = pix(:);
        if pix < 25 % black = wall
            % TODO (skip)
        elseif pix > 100 % white = blank space
            % TODO (skip)
        else
            %diff1 = abs(pix(1) - pix(2));
            %diff2 = abs(pix(2) - pix(3));
            %if diff1 < 25 && diff2 < 25 % gray (all values similar)
            %    bitmap(r, c, 2) = 255;
            if pix(3) > 200 % dominant blue = hallway
                bitmap(r, c) = HALLWAY;
            elseif pix(1) > 200 % dominant red = staircase
                bitmap(r, c) = STAIRCASE;
            end
        end
    end
end

clear h w;

subplot(2, 1, 1);
imshow(img);
subplot(2, 1, 2);
imshow(uint8(bitmap * 100));