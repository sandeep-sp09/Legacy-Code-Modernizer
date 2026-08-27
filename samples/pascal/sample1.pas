program Sample1;
var
  x, y, sum: integer;

function AddNumbers(a, b: integer): integer;
begin
  AddNumbers := a + b;
end;

begin
  x := 5;
  y := 10;
  sum := AddNumbers(x, y);
  writeln('Sum is: ', sum);
end.
