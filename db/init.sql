-- Create the known_plates table
CREATE TABLE IF NOT EXISTS known_plates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL UNIQUE
);

-- Create the detected_plates table
CREATE TABLE IF NOT EXISTS detected_plates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_known BOOLEAN NOT NULL,
    image_path VARCHAR(255)
);

-- Insert some known license plates
INSERT INTO known_plates (license_plate) VALUES
-- ('VHK-1164'),
-- ('JA62 UAR'),
('R96-0YR'),
('PG-MN112');