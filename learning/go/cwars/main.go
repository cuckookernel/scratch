package main

import "fmt"

func main() {
   // fmt.Println("Hellows")
   fmt.Println("din:", DuplicateEncode("din"))

   fmt.Println("toWeirdCase:", toWeirdCase("This is a test Looks like you passed"))

   fmt.Println(TowerBuilder(5))

   // fmt.Println("ip_validation:", Is_valid_ip("12.12.12.089"))

   fmt.Println(ToCamelCase("the-brown_fox"))

   arr := []int{12, 10, 8, 8, 3, 3, 3, 3, 2, 4, 10, 12, 10}
   // arr := []int{10, 10, 20, 20}
   fmt.Println(HighestRank(arr))

   fmt.Println("gta:", Gta(7, []int{12348, 5, 67}))

}
