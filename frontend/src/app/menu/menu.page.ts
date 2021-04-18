import { Component, OnInit } from '@angular/core';
import { Router, NavigationExtras } from '@angular/router';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.page.html',
  styleUrls: ['./menu.page.scss'],
})
export class MenuPage implements OnInit {

  constructor(private router: Router) { }

  ngOnInit() {
  }

  creteGame() {
    console.log("Creating new game!");
    let navigationExtras: NavigationExtras = {
      state: {
        createGame: true
      }
    };
    this.router.navigate(['game'], navigationExtras);
  }

  joinGame() {
    console.log("Joining existing game!");
    let navigationExtras: NavigationExtras = {
      state: {
        createGame: false
      }
    };
    this.router.navigate(['game'], navigationExtras);
  }

  showAlert() {
    alert("It's not yet implemented!");
  }

}
