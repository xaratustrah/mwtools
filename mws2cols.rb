#!/usr/bin/env ruby
# Convert MWS multi parameteric plots to columns
#
# Xaratustrah 2012
#

file = File.new(ARGV[0], "r")
out1= Array.new
out2 = Array.new

while (line = file.gets)
line=line.split(/\s/)

line.each do |x|
out1 << x if x.to_s.match /\d/
end

end
file.close

out1.each {|x| out2 << x if not x.to_s == "1" and not x.to_s == "2"}

i = 0
while (i <= out2.size - 1)
str = out2[i].gsub!("/real", "")
print ("#{str}, #{out2[i+1]}, #{out2[i+2]} \n")
i = i + 3
end